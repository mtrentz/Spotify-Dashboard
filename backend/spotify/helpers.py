from .models import UserActivity
from datetime import timedelta, datetime
from rest_framework.exceptions import ParseError
from .models import Tracks, SearchHistory
import logging
import pytz

logger = logging.getLogger("django")


def find_track_in_database(track_name, artist_name):
    """
    Just like when searching for songs on Spotify API I will try to remove the " - Remaster", " - Live", etc...
    Here I will do the same when searching for tracks in the database.

    This is used only for inserting HISTORY, since then I only have the track and artists name,
    and have no ID.
    """
    # First I try searching for the exact name in the database
    tracks = Tracks.objects.filter(name=track_name, artists__name=artist_name)

    # If found, just return it
    if tracks:
        return tracks

    # If nothing was found, maybe this exact track_name and artist_name were searched before
    # on Spotify's search API. So I will just check for this in my search history.
    searched = SearchHistory.objects.filter(
        track_name=track_name, artist_name=artist_name
    )

    # If wasnt searched before
    if not searched:
        # Tracks is an empty queryset.
        return tracks

    # Since on the SearchHistory I store only the track sp_id (because tracks are searched before being added into the database)
    # now I still have to use the sp_id to retrieve the Track object
    tracks = Tracks.objects.filter(sp_id=searched[0].track_sp_id)

    # Return the tracks.
    # There is a small chance that for some reason the track_name was added to SearchHistory and not added to the database.
    # In this case I will have gotten an empty queryset when retrieving with its sp_id.
    # It makes complete sense to just return an empty queryset here if nothing was found.
    return tracks


def search_spotify_track(sp, track_name, artist_name, type):
    # This usually removes the "... - Remaster" or "...  - Live"
    non_remaster_track = track_name.split(" - ")[0]

    # Make list of possible queries
    queries = [
        # Try normally forcing track name and artist name
        f"track:{track_name} artist:{artist_name}",
        # Try not forcing track/artist
        f"{track_name} {artist_name}",
        # Try without remaster
        f"track:{non_remaster_track} artist:{artist_name}",
        # Try with track name only
        f"track:{track_name}",
    ]

    for q in queries:
        # Try searching for the query
        track = try_searching(sp, q, type)
        if track:
            # If I ever find a track after searching for it,
            # I will keep the record on my SearchHistory, so I will never
            # have to make the same search again.
            SearchHistory.objects.create(
                track_name=track_name,
                artist_name=artist_name,
                track_sp_id=track["id"],
            )
            return track

    # If not found, return None
    return None


def try_searching(sp, query, type):
    # If yet not got a response, search only with track name
    track = sp.search(
        q=query,
        type=type,
        limit=1,
    )

    # Check if got a response
    items = track["tracks"]["items"]
    if len(items) > 0:
        return items[0]

    # If yet not found, return None
    return None


def get_equivalent_user_activities(track, played_at):
    """
    Will return the UserActivity of any of the same track played 1 minute before or after the given time
    """
    minute_offset = 1
    lower_limit = played_at - timedelta(minutes=minute_offset)
    upper_limit = played_at + timedelta(minutes=minute_offset)

    user_activities = UserActivity.objects.filter(
        track__sp_id=track.sp_id, played_at__range=[lower_limit, upper_limit]
    )
    return user_activities


def user_activities_are_equal(ua1, ua2):
    if ua1.from_import == ua2.from_import:
        if ua1.track.sp_id == ua2.track.sp_id:
            if ua1.ms_played == ua2.ms_played:
                if ua1.played_at == ua2.played_at:
                    return True
    return False


def insert_user_activity(track, ms_played, played_at, from_import):
    """
    This is a bit more complicated than simply checking for exact match in database.

    When tracks come from the 'import', which means you downloaded directly through spotify your history
    of the last 9 months, tracks that were not listened to 100% will still be included. But when querying
    for recently played tracks in Spotify's API, only tracks that were listened through fully will be returned.

    Besides that, when tracks comes from the import the 'played_at' is calculated from the end time, which is not very precise.
    """

    # I use this function both for Celery and running normally.
    # Aparently when it comes from Celery the "played_at" is formated as string.
    # So I will check and convert it to datetime if needed.
    if isinstance(played_at, str):
        try:
            played_at = datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            # Some history data seems to be formated differently
            played_at = datetime.strptime(played_at, "%Y-%m-%dT%H:%M:%S%z")
        except Exception as e:
            logger.error(f"Error converting played_at to datetime: {e}")
            return

    incoming_activity = UserActivity(
        track=track,
        ms_played=ms_played,
        played_at=played_at,
        from_import=from_import,
    )

    artists = track.artists.all()
    artists_names = [a.name for a in artists]
    logger.info(f"Trying to insert user activity for {track.name} - {artists_names}")

    # Check if there are any equivalent acitivies (more or less the same time played for the same track)
    equivalent_activities = get_equivalent_user_activities(track, played_at)

    # If there isnt any equivalent activity, insert the new one and exit function
    if not equivalent_activities:
        incoming_activity.save()
        return

    # If there is, loop through them and check if there is one thats exactly the same
    for equivalent_activity in equivalent_activities:
        if user_activities_are_equal(incoming_activity, equivalent_activity):
            # If it is, exit function
            return

    # If none of them were exactly equal, then some assumptions will be needed.
    # Usually the user activity will either be new or exactly equals as a existing one,
    #   so it's not often that the code will reach here.

    # Another possible case is that there was a rounding error when one track comes from the history
    #   and another were is coming through the Recently Played API Endpoint.
    # I'll loop through them and check for this case
    for equivalent_activity in equivalent_activities:
        if equivalent_activity.from_import and not incoming_activity.from_import:
            # In this case, the incoming one has more accurate data, since it comes from the API,
            # so I'll update the existing one to match it
            equivalent_activity.track = incoming_activity.track
            equivalent_activity.ms_played = incoming_activity.ms_played
            equivalent_activity.played_at = incoming_activity.played_at
            equivalent_activity.from_import = incoming_activity.from_import
            equivalent_activity.save()
            # I will exit the function!
            # There is a chance that the next one (in case there were many equivalent)
            #   would also match this condition.
            # But I have no way of telling which one is "more right" to update.
            # And updating both of them is definitely wrong.
            # So I will just update this first one and exit this function.
            return

        # If it is the other way around, the equivalent one being from the API and the incoming from the import.
        if not equivalent_activity.from_import and incoming_activity.from_import:
            # In this case, I want to do nothing. Since I already have the most accurate data.

            # First I'll check if there isn't another equivalent activity
            if equivalent_activity == equivalent_activities[-1]:
                # In this case, this is the last one. And I know its a rounding error
                #  since one is from the history and another isnt.
                # So I'll just return and don't try anything else
                return
            # If there are more equivalent activities to check, I'll just continue
            continue

    # If it gets here there are two possibilities;
    #  1. Both of them are from history, but not exactly the same track.
    #  2. Both are from the API, but not exactly the same track.

    # In this case, I'll just add the incoming one to the database.
    # This probably happened because the track was very short.
    logger.info(
        f"Track {track.name} sp_id {track.sp_id} played for {ms_played} at {played_at} got to the last point when inserting User Activity."
    )
    incoming_activity.save()


def validate_days_query_param(days):
    try:
        days = int(days)
    except ValueError:
        raise ParseError("days must be an integer")
    if days < 0:
        raise ParseError("days must be positive")
    return days


def validate_qty_query_params(qty):
    try:
        qty = int(qty)
    except ValueError:
        raise ParseError("qty must be an integer")
    if qty < 0:
        raise ParseError("qty must be positive")
    return qty


def validate_timezone_query_params(tz_name):
    if tz_name not in pytz.all_timezones:
        logger.warning(f"Invalid timezone: {tz_name}")
        return "UTC"
    return tz_name


def unpack_response_images(imgs_resp):
    """
    This is going to unpack all the images URL from the spotify response
    and order it into image_sm, image_md, image_lg.

    It's going to be used for both artists and album.
    """
    # Start all values at none
    image_sm, image_md, image_lg = None, None, None

    data = []

    for img_data in imgs_resp:
        # As far as I know, all images are square on spotify. So I'll just store one dimension.
        height = img_data.get("height")
        url = img_data.get("url")
        data.append((height, url))

    # Sort the data by height, from lower to higher
    data.sort(key=lambda x: x[0])

    # Remove any tuple in Data if one of the values (height or url) is None
    data = [x for x in data if x[0] and x[1]]

    # Assign the images to the variables
    if data:
        image_sm = data[0][1]
        if len(data) > 1:
            image_md = data[1][1]
            if len(data) > 2:
                image_lg = data[2][1]

    return image_sm, image_md, image_lg
