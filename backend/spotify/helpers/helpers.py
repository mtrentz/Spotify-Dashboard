from ..models import UserActivity


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


def insert_user_activity(track, ms_played, played_at, from_import):
    # TODO: Aqui tenho que pensar como vai funcionar quando ja existir uma track
    # com um tempo um pouco diferente. Pq há aqla diferença entre historico e recently played
    # If exists, returns empty

    user_activity, created = UserActivity.objects.get_or_create(
        track=track,
        played_at=played_at,
        ms_played=ms_played,
        from_import=from_import,
    )
