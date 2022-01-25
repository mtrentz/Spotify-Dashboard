from celery import shared_task, Task
from django.forms import ValidationError
from .serializers.insert_serializers import TrackEntrySerializer
from .models import Artists, Genres, Albums, Tracks
from .helpers import (
    search_spotify_track,
    insert_user_activity,
    unpack_response_images,
    find_track_in_database,
)
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rest_framework.exceptions import NotFound, ValidationError
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger("django")

# dev only
from dotenv import load_dotenv


class LogErrorsTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception("Celery task failure; ", exc_info=exc)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@shared_task(base=LogErrorsTask)
def insert_track_entry(track_entry_data):
    """
    Gets proper track entry data dictionary and insert it into the database.

    This function calls the Spotify API a few times, so it's going to be sent to background
    every time.

    It then runs sequentially, querying the spotify API for artist of the track, then album of
    the track. Finally, it adds everything into the database.
    """
    # Unpack some of the data that I will need for the first check
    track_sp_id = track_entry_data["track_sp_id"]
    played_at = track_entry_data["played_at"]
    ms_played = track_entry_data["ms_played"]
    from_import = track_entry_data["from_import"]

    # Before everything else I will check if the track already exists in the database
    tracks = Tracks.objects.filter(sp_id=track_sp_id)
    # If it exists, I only need to add it to UserActivity and exit!
    if tracks:
        track = tracks.first()
        insert_user_activity(
            track=track,
            played_at=played_at,
            ms_played=ms_played,
            from_import=from_import,
        )
        return

    # In case it wasn't in the database, then I'll have to do a bunch of queries to get all the data
    load_dotenv()
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(cache_handler=None)
    )

    ### ARTISTS
    artists_sp_ids = track_entry_data["artists_sp_ids"]
    artists = []
    for artist_sp_id in artists_sp_ids:
        # First check if artist already exists in database
        artist = Artists.objects.filter(sp_id=artist_sp_id).first()
        # If exists
        if artist:
            # Just append it to list and continue to next iteration
            artists.append(artist)
            continue

        artist_response = sp.artist(artist_sp_id)
        logger.info(
            f"[API Call] Artist: sp_id: {artist_sp_id}, name: {artist_response.get('name')}"
        )

        artist_name = artist_response.get("name")
        artist_popularity = artist_response.get("popularity")
        artist_followers = artist_response.get("followers").get("total")

        # Artist images
        artist_images = artist_response.get("images")
        # Unpack them by size. Helper function since the same logic is used for album art
        artist_art_sm, artist_art_md, artist_art_lg = unpack_response_images(
            artist_images
        )

        # Here since we only add if the artist with same sp_id doesn't exist,
        # what happens is that the popularity and follower numbers will never be updated.
        # But I don't think that is a problem.
        artist, _ = Artists.objects.get_or_create(
            sp_id=artist_sp_id,
            name=artist_name,
            popularity=artist_popularity,
            followers=artist_followers,
            art_sm=artist_art_sm,
            art_md=artist_art_md,
            art_lg=artist_art_lg,
        )
        artists.append(artist)

        genres = artist_response.get("genres")
        # Add genres to database
        for genre in genres:
            genre, _ = Genres.objects.get_or_create(name=genre)
            artist.genres.add(genre)

    # Having at least one artists is required. If none were found, exits
    if not artists:
        logger.error(f"No artists found for track {track_sp_id}")
        raise NotFound(detail="No artists found for Track Entry")

    ### ALBUM
    album_sp_id = track_entry_data["album_sp_id"]

    # First check if album already exists in database
    album = Albums.objects.filter(sp_id=album_sp_id).first()
    # If not exist, query it from Spotify, and save it
    if not album:
        album_response = sp.album(album_sp_id)
        logger.info(
            f"[API Call] Album: sp_id: {album_sp_id}, name: {album_response.get('name')}"
        )

        album_name = album_response.get("name")
        album_popularity = album_response.get("popularity")
        album_total_tracks = album_response.get("total_tracks")
        album_type = album_response.get("album_type")

        # Album images
        album_images = album_response.get("images")
        # Unpack them by size. Helper function since the logic is the same for artists images.
        album_art_sm, album_art_md, album_art_lg = unpack_response_images(album_images)

        album_release_date = album_response.get("release_date")
        album_release_date_precision = album_response.get("release_date_precision")

        if album_release_date_precision == "year":
            album_release_date = datetime.strptime(album_release_date, "%Y")
        elif album_release_date_precision == "month":
            album_release_date = datetime.strptime(album_release_date, "%Y-%m")
        else:
            album_release_date = datetime.strptime(album_release_date, "%Y-%m-%d")

        # Here since we only add if an album with same sp_id doesn't exist,
        # what happens is that the popularity of the album will never be updated.
        # But I don't think that is a problem.
        album, _ = Albums.objects.get_or_create(
            sp_id=album_sp_id,
            name=album_name,
            popularity=album_popularity,
            release_date=album_release_date,
            total_tracks=album_total_tracks,
            type=album_type,
            art_sm=album_art_sm,
            art_md=album_art_md,
            art_lg=album_art_lg,
        )

        # Add artists to album (many to many)
        album.artists.add(*artists)

    ### TRACK
    # Here I don't have to query spotify, since I already have all the info I need
    track_name = track_entry_data["track_name"]
    track_duration = track_entry_data["track_duration"]
    track_popularity = track_entry_data["track_popularity"]
    track_explicit = track_entry_data["track_explicit"]
    track_number = track_entry_data["track_number"]
    track_disc_number = track_entry_data["track_disc_number"]
    track_type = track_entry_data["track_type"]

    # There is a small problem here that the popularity will never be updated
    # but I don't think it matters.
    track, _ = Tracks.objects.get_or_create(
        sp_id=track_sp_id,
        name=track_name,
        duration=track_duration,
        popularity=track_popularity,
        explicit=track_explicit,
        track_number=track_number,
        disc_number=track_disc_number,
        type=track_type,
        album=album,
    )
    track.artists.add(*artists)

    ### User Activity
    # Here I will check if need to add to user activity.
    # There are some extra considerations to be made, which will be explained in the function
    insert_user_activity(
        track=track,
        played_at=played_at,
        ms_played=ms_played,
        from_import=from_import,
    )


@shared_task(base=LogErrorsTask)
def insert_track_batch_from_history(batch):
    """
    This serves just as a wrapper for the insert_track_from_history function.

    Since executing one Task is too intensive for celery/redis,
    doing this is batches proved to be way faster.
    """
    for data in batch:
        insert_track_from_history(
            track_name=data["track_name"],
            artist_name=data["artist_name"],
            end_time=data["end_time"],
            ms_played=data["ms_played"],
        )


@shared_task(base=LogErrorsTask)
def insert_track_from_history(
    track_name,
    artist_name,
    end_time,
    ms_played,
):
    """
    This function will get everything needed to insert a track into the database
    from the track name, history name, end time and miliseconds played
    which are the info that the spotify history provides.

    It will first check for an existing track in the database,
    if there aren't any, it will query the spotify API for all the
    info needed.
    """

    # Neeed to calculate 'played_at' if I want to add to UserActivity
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
    played_at = end_time_dt - timedelta(milliseconds=ms_played)
    # Pass it to UTC
    played_at = played_at.replace(tzinfo=pytz.UTC)

    # Here I try looking for the track in the database in diferent ways than just name matching.
    tracks = find_track_in_database(track_name=track_name, artist_name=artist_name)

    # If track was already in the database, just add to UserActivity
    if tracks.exists():
        track = tracks.first()

        # Will check if not already in UserActivity also
        try:
            insert_user_activity(
                track=track,
                played_at=played_at,
                ms_played=ms_played,
                from_import=True,
            )
        except Exception as e:
            logger.error(
                f"Error inserting UserActivity for track {track.sp_id} played at {played_at}: {e}"
            )
        return

    # If not, I will try to find it in Spotify

    # TODO: Tirar isso no futuro
    load_dotenv()
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    # Search song on Spotify
    track_resp = search_spotify_track(sp, track_name, artist_name, "track")

    # If not found song on spotify, exits
    if not track_resp:
        logger.debug(f"No track found when searching for {track_name} by {artist_name}")
        return

    artists = track_resp.get("artists")
    artists_sp_ids = [a.get("id") for a in artists]

    track_entry_data = {
        "album_sp_id": track_resp.get("album").get("id"),
        "artists_sp_ids": artists_sp_ids,
        "track_sp_id": track_resp.get("id"),
        "track_name": track_resp.get("name"),
        "track_duration": track_resp.get("duration_ms"),
        "track_popularity": track_resp.get("popularity"),
        "track_explicit": track_resp.get("explicit"),
        "track_number": track_resp.get("track_number"),
        "track_disc_number": track_resp.get("disc_number"),
        "track_type": track_resp.get("type"),
        # Pass the data from history
        "played_at": played_at,
        "ms_played": ms_played,
        "from_import": True,
    }

    # Check if track_entry_data is valid before sending to the add task
    serializer = TrackEntrySerializer(data=track_entry_data)
    if not serializer.is_valid():
        raise ValidationError(serializer.errors)

    # Now that I have the full track entry data, send it to the insert_track_entry task.
    # Won't call .delay in this task because I want to run it sequentially.
    insert_track_entry(track_entry_data)
