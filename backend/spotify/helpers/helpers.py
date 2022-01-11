from ..models import UserActivity
from datetime import timedelta


def search_spotify_song(sp, track_name, artist_name, type):
    # This usually removes the "... - Remaster" or "...  - Live"
    non_remaster_track = track_name.split(" - ")[0]

    # Make list of possible queries
    queries = [
        # Try normally forcing track name and artist name
        f"track:{track_name} artist:{artist_name}",
        # Try without remaster
        f"track:{non_remaster_track} artist:{artist_name}",
        # Try not forcing track/artist
        f"{track_name} {artist_name}",
        # Try with track name only
        f"track:{track_name}",
    ]

    for q in queries:
        # Try searching for the query
        track = try_searching(sp, q, type)
        # If found, return it
        if track:
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


def get_equivalent_user_activity(track, played_at):
    """
    Will return the UserActivity of any of the same track played 1 minute before or after the given time
    """
    minute_offset = 1
    lower_limit = played_at - timedelta(minutes=minute_offset)
    upper_limit = played_at + timedelta(minutes=minute_offset)

    user_activity = UserActivity.objects.filter(
        track__sp_id=track.sp_id, played_at__range=[lower_limit, upper_limit]
    ).first()
    return user_activity


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
    user_activity = UserActivity(
        track=track,
        ms_played=ms_played,
        played_at=played_at,
        from_import=from_import,
    )

    # CHECK IF THERE ARE ANY EQUIVALENT USER ACTIVITIES
    equivalent_activity = get_equivalent_user_activity(track, played_at)

    # IF THERE ISNT ANY, JUST ADD IT AND RETURN
    if not equivalent_activity:
        user_activity.save()
        return

    # IF THERE IS, CHECK IF ITS EQUAL WITH THE INCOMING ONE
    # IF IT IS EQUAL, RETURN BECAUSE THERE IS NOTHING ELSE TO DO
    if user_activities_are_equal(user_activity, equivalent_activity):
        return

    # CHECK IF INCOMING IS FROM RECENTLY PLAYED
    if not user_activity.from_import:
        # IF IT IS NOT, CHECK IF THE EQUIVALENT IS FROM SPOTIFY HISTORY
        if equivalent_activity.from_import:
            # IF SO, UPDATE THE EQUIVALENT ONE TO BE EQUAL THE INCOMING.
            # This is becasue the incoming one (from recently played) is more accurate
            equivalent_activity.track = user_activity.track
            equivalent_activity.ms_played = user_activity.ms_played
            equivalent_activity.played_at = user_activity.played_at
            equivalent_activity.from_import = user_activity.from_import
            equivalent_activity.save()
            return
        # IF IS NOT, SHOULD NEVER HAPPEN BUT ADD THE INCOMING TO THE DB.
        else:
            # If it gets here means that both are from recently played (very accurate, and only for tracks 100% listened to).
            # This could only happen if songs are < 1 min of length. If so, just add it to database
            user_activity.save()
            return

    # IF NOT, THEN INCOMIG IS FROM HISTORY
    # IF EQUIVALENT IS ALSO FROM HISTORY, THIS SHOULD NOT HAPPEN, BUT ADD TO DB
    if equivalent_activity.from_import:
        # It only gets here if both are from history. Which means that they were listened to different time stamps in a span of 1min
        # And also listened to fully. Add it to database
        user_activity.save()
        return
    else:
        # Gets here if incoming is from history and equivalent is from recently played.
        # If so, there are two possibilities:
        # 1. They are exactly the same entry (same song listened to at the same time), but its a rounding error
        #       when calculating the played_at for the incoming one (from history);
        # 2. It is a very short track. But the one existing was listened to fully (it has to) and the incoming one was not.
        #      This seems very unlikely.
        # So, assuming its a rounding error, I do nothing
        return
