from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
import json
from ..models import UserActivity
from ..serializers.insert_serializers import (
    TrackEntrySerializer,
    HistoryFileSerializer,
    HistoryEntrySerializer,
)
from .auth_views import BaseAuthView
from ..tasks import (
    insert_track_entry,
    insert_track_batch_from_history,
)
import logging

logger = logging.getLogger("django")


class ImportStreamingHistoryView(APIView):
    def post(self, request):

        serializer = HistoryFileSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(serializer.errors)
            raise ValidationError(serializer.errors)

        # Accepts multiple streaming history files
        file_list = request.data.getlist("file")

        data_list = []

        try:
            for file in file_list:
                data_list.extend(json.loads(file.read()).copy())
        except Exception as e:
            raise ValidationError(f"Invalid Streaming History JSON file; {e}")

        # TODO: When its not that many entries, batch is not needed
        # since it makes it slower, because all requests will run single threaded

        # I'll send the data to Celery, to run in the background,
        # in batches. This is because it takes too long to create
        # one Task per entry.
        batch = []

        # I have to choose a batch size. When it's too small, it will take too long
        # because then too many TASKS will be created for celery to run.
        # But when its too few, then all requests will be running
        # in the same thread, which will be too slow.
        if len(data_list) < 50:
            batch_size = 1
        elif len(data_list) < 500:
            batch_size = 10
        elif len(data_list) < 1000:
            batch_size = 100
        else:
            batch_size = 200

        for data in data_list:
            history_entry_serializer = HistoryEntrySerializer(data=data)

            # If not valid for some reason, I print error and continue
            if not history_entry_serializer.is_valid():
                logger.warning(history_entry_serializer.errors)
                continue

            # Won't let duplicates be added into Streaming History
            history_entry_serializer.save()

            batch.append(
                {
                    "track_name": data.get("trackName"),
                    "artist_name": data.get("artistName"),
                    "end_time": data.get("endTime"),
                    "ms_played": data.get("msPlayed"),
                }
            )

            # Send to celery every few entries
            if len(batch) >= batch_size:
                insert_track_batch_from_history.apply_async(args=[batch], countdown=5)
                batch = []

        # Send the remaining tracks
        if batch:
            insert_track_batch_from_history.apply_async(args=[batch], countdown=5)

        return Response(
            {"Success": "History is being added into the database."},
            status=status.HTTP_201_CREATED,
        )


class RecentlyPlayedView(BaseAuthView):
    """
    The main purpose of this View is having a method that I can call on my scheduler.

    Done this way to properly inherit from BaseAuthView.

    Also has a post method that can be called from frontend to force a refresh of the recently played tracks.
    """

    def post(self, request):
        self.insert_recently_played()
        return Response(
            {"Success": "Your recently played tracks are being added to the database."},
            status=status.HTTP_201_CREATED,
        )

    def insert_recently_played(self):
        """
        Requests and loops through all recently played song not before added to UserActivity.
        For new songs, send it to TrackEntrySerializer, where all data needed will be requested and then stored to UserActivity
        """

        try:
            recently_played = self.sp.current_user_recently_played(limit=50)
        except Exception as e:
            # Error here means it's not authorized, so I'll just reset token info
            self.sp.auth_manager.cache_handler.save_token_to_cache({})
            logger.error(f"Error getting recently played: {e}")
            raise PermissionDenied(
                f"Error trying to get recently played; Most likely not authorized."
            )
        querying_new_songs = True

        while querying_new_songs:
            # Items come ordered from most recent to oldest
            for item in recently_played["items"]:
                track = item.get("track")
                played_at = item.get("played_at")
                track_sp_id = track.get("id")

                # TODO: Offload these to the background?

                # Check if there is already an exact entry for this song on the database
                if UserActivity.objects.filter(
                    track__sp_id=track_sp_id, played_at=played_at
                ).exists():
                    continue

                # Get the list of artists
                artists = track.get("artists")
                # Get all artists ids
                artists_sp_ids = [artist.get("id") for artist in artists]

                track_entry_data = {
                    "album_sp_id": track.get("album").get("id"),
                    "artists_sp_ids": artists_sp_ids,
                    "track_sp_id": track_sp_id,
                    "track_name": track.get("name"),
                    "track_duration": track.get("duration_ms"),
                    "track_popularity": track.get("popularity"),
                    "track_explicit": track.get("explicit"),
                    "track_number": track.get("track_number"),
                    "track_disc_number": track.get("disc_number"),
                    "track_type": track.get("type"),
                    "played_at": played_at,
                    # Tracks that come from Recently Played were always listened to fully.
                    "ms_played": track.get("duration_ms"),
                    "from_import": False,
                }

                serializer = TrackEntrySerializer(data=track_entry_data)

                if serializer.is_valid():
                    # If the serializer is valid, I'll send the track entry data
                    # to a celery task, which will run everything in the
                    # background.
                    insert_track_entry.delay(track_entry_data)

            # If it got here without "query_new_songs" being set to False, it means that there are more songs to be queried
            if recently_played["next"]:
                # PS: This seems to not work. Spotify seems to always return an empty list.
                recently_played = self.sp.next(recently_played)
            else:
                # If there were no "next" in response, then just stop the while loop
                querying_new_songs = False
