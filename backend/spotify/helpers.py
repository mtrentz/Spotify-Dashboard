from .models import UserActivity
from rest_framework.exceptions import ValidationError
from datetime import timedelta, datetime
from rest_framework.exceptions import ParseError
from .models import Tracks, SearchHistory
from django.db.models.functions import Trunc
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
    resp = sp.search(
        q=query,
        type=type,
        limit=1,
    )
    logger.info(f"[API Call] Made SEARCH for: {query}")

    # Check if got a response
    items = resp["tracks"]["items"]
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

    For this reason, I'll apply some logic when a track is being inserted FROM HISTORY and there was another very similar entry FROM RECENTLY PLAYED.
    The same happens when a track is being inserted FROM RECENTLY PLAYED and there was another very similar entry FROM HISTORY.
    If all the tracks were coming in from the same source, then there would be no problem.

    So my checks here are first to see if there is a similar track. If there isnt, then it's easy, just add it.
    If there is, then I can start checking for exact matches. If there is an exact match, then it's also easy, just do nothing!
    But if there is no exact match and there are similar tracks, then I'll check if they come from different sources. If they do,
    then some logic and assumptions will be needed. If they come from the same source, i'll just add the incoming one as new.
    """

    # I use this function both for Celery and running normally.
    # So I'll just convert the string to date,
    # since it gets converted to string in celery.
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


def validate_year_query_param(year):
    try:
        year = int(year)
    except ValueError:
        raise ParseError("Year must be an integer")
    if year <= 1970:
        raise ParseError("Year must be after 1970")
    return year


def validate_date_query_param(date):
    """
    Accepts date as a string in the format of YYYY-MM-DD
    """
    try:
        date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ParseError("Date must be in the format of YYYY-MM-DD")
    return date


def validate_qty_query_params(qty):
    try:
        qty = int(qty)
    except ValueError:
        raise ParseError("qty must be an integer")
    if qty < 0:
        raise ParseError("qty must be positive")
    return qty


def validate_and_parse_date_selection_query_parameters(
    days, year, date_start, date_end
):
    """
    This is the main function that will do the logic for validating the date parameters
    that many endpoint will receive.

    Some endpoints will have the possibility of filtering by:
        days: The amount of days in the past to include in the query.
        year: The single year to include in the query.
        date_start, date_end: Range of dates to be included in the query.

    These types of filtering are exclusive. Meaning only one can be chosen.

    This function will check if more than one of them were passed through as query parameters
    and return an error if so.

    If everthing is valid, it will return the query parameters back, with None for those that were not passed.
    And will also return the method which the query has to be made. The possible methods are
    "days", "year", "date_range" or None if no date parameter was passed.

    Returns:
        tuple: (days, year, date_start, date_end, method)
    """

    amount_params = sum([bool(days), bool(year), (bool(date_start) or bool(date_end))])

    # First I will check if not too many parameters were passed
    if amount_params > 1:
        raise ParseError(
            "You can only pass one of the following parameters: days, year, [date_start, date_end]"
        )

    # I will also check if no parameter was passed
    if amount_params == 0:
        return None, None, None, None, None

    # If days was passed, I'll validate it and return it
    if days:
        days = validate_days_query_param(days)
        return days, None, None, None, "days"

    # If year was passed, I'll validate it and return it
    if year:
        year = validate_year_query_param(year)
        return None, year, None, None, "year"

    # If date_start or date_end was passed, I'll validate them and return them
    if date_start:
        date_start = validate_date_query_param(date_start)

    if date_end:
        date_end = validate_date_query_param(date_end)

    if date_start == date_end:
        raise ParseError("date_start and date_end cannot be the same")

    # If one of date_start, date_end wasn't passed, it will still be returned as None
    return None, None, date_start, date_end, "date_range"


def validate_timezone_query_params(tz_name):
    if tz_name not in pytz.all_timezones:
        logger.warning(f"Invalid timezone: {tz_name}")
        return "UTC"
    return tz_name


def filter_model_by_date_selection(
    model,
    tzinfo,
    days_param,
    year_param,
    date_start_param,
    date_end_param,
    method,
    path_to_played_at,
):
    """
    As well as validating the types of date filtering that will be done, the process of
    filtering a table for the queryset is also common in many endpoints.

    So here a model will be filtered depending on the date parameters sent to the endpoint.

    The tricky argument is "path_to_played_at", which should be a django query to get to the played_at field.
    For example "tracks__useractivity__played_at"

    It will return a queryset.
    """
    # First I have to see which method is going to be used for filtering
    if method == "year":
        objects = model.objects.annotate(
            year=Trunc(path_to_played_at, "year", tzinfo=tzinfo)
        ).filter(year__year=year_param)
    else:
        # All other methods share the same logic of filtering by date range
        # If no method is passed, the default will be returning the last 7 days
        if method == "days" or method == None:
            if method == None:
                days_param = 7
            date_now = datetime.now(tzinfo)
            # Defines date start and end for filtering
            date_start = date_now - timedelta(days=days_param)
            date_end = date_now
        elif method == "date_range":
            # I have to check if both date_start and date_end were passed
            # If no start, set it to 7 days ago
            if not date_start_param:
                date_start_param = datetime.now(tzinfo) - timedelta(days=7)
            # If no end, set it to now
            if not date_end_param:
                date_end_param = datetime.now(tzinfo)

            date_start = date_start_param
            date_end = date_end_param
            # Add tz info to dates
            date_start = date_start.replace(tzinfo=tzinfo)
            date_end = date_end.replace(tzinfo=tzinfo)
        # Should never get here, but just in case...
        else:
            raise ValidationError(
                "Invalid method parameter. Valid values are: days, year, date_range"
            )
        # Filter by range
        # I have to pass the path to the played_at_field__range
        kwargs = {path_to_played_at + "__range": [date_start, date_end]}

        objects = model.objects.filter(**kwargs)

    # Returns the queryset filtered by date
    return objects


def filter_model_by_date_selection_previous_period(
    model,
    tzinfo,
    days_param,
    year_param,
    date_start_param,
    date_end_param,
    method,
    path_to_played_at,
):
    """
    Very similar to the normal filter by date selection, but has extra logic to get the previous period.
    """
    if method == "year":
        # Get 1 year before
        previous_objects = model.objects.annotate(
            year=Trunc(path_to_played_at, "year", tzinfo=tzinfo)
        ).filter(year__year=year_param - 1)
    else:
        # Here, all other methods filter by range
        if method == "days" or method == None:
            # If no parameter was passed, default to last 7 days
            if method == None:
                days_param = 7
            # For previous period, the start is now - 2 * days_param ago
            previous_date_start = datetime.now(tzinfo) - timedelta(days=2 * days_param)
            # The end is now - days_parm ago
            previous_date_end = datetime.now(tzinfo) - timedelta(days=days_param)
        elif method == "date_range":
            # I have to check if both date_start and date_end were passed
            # If no start, set it to 7 days ago
            if not date_start_param:
                date_start_param = datetime.now(tzinfo) - timedelta(days=7)
            # If no end, set it to now
            if not date_end_param:
                date_end_param = datetime.now(tzinfo)
            # Get the amount of days between dates
            days_diff = (date_end_param - date_start_param).days
            # For previous period just subtract the days_diff
            previous_date_start = date_start_param - timedelta(days=days_diff)
            previous_date_end = date_end_param - timedelta(days=days_diff)
            # Add tz info to dates
            previous_date_start = previous_date_start.replace(tzinfo=tzinfo)
            previous_date_end = previous_date_end.replace(tzinfo=tzinfo)
        # Should never get here, but just in case...
        else:
            raise ValidationError(
                "Invalid method parameter. Valid values are: days, year, date_range"
            )
        # Filter by range
        kwargs = {
            path_to_played_at + "__range": [previous_date_start, previous_date_end]
        }
        previous_objects = model.objects.filter(**kwargs)

    return previous_objects


def calculate_growth(previous_value, current_value):
    """
    Calculates the growth between two values.
    """
    if previous_value == 0:
        return 0
    return (current_value - previous_value) / previous_value


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


def make_filter(model, **kwargs):
    print(model.objects.filter(**kwargs))


def make_filter_two(model, arg_kw, d1, d2):
    args = {arg_kw: [d1, d2]}
    print(model.objects.filter(**args))
