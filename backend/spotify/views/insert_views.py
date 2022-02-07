from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied, NotAcceptable
import json
from ..models import UserActivity
from ..serializers.insert_serializers import (
    TrackEntrySerializer,
    HistoryFileSerializer,
    HistoryEntrySerializer,
)
from .auth_views import BaseAuthView
from ..tasks import (
    insert_track_batch_from_list,
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

        # Unpack the data into a list, because this way its pretty fast for
        # celery to serialize it.
        batch_data = [
            [
                d.get("trackName"),
                d.get("artistName"),
                d.get("endTime"),
                d.get("msPlayed"),
            ]
            for d in data_list
        ]

        # Send it to celery
        insert_track_batch_from_list.apply_async(args=[batch_data], countdown=5)

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
        try:
            self.insert_recently_played()
        except PermissionDenied:
            # If I got an PermissionDenied I want to return a different response
            # otherwise the frontend will think its a authentication error with
            # the login system, and not the spotify official API.
            # In this case I'll return a NotAcceptable
            raise NotAcceptable(
                "Failed getting recently played tracks. Please check if you've authorized the app."
            )

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
            logger.info(f"[API Call] Query for recenltly played tracks")

        except Exception as e:
            # Error here means it's not authorized, so I'll just reset token info
            # self.sp.auth_manager.cache_handler.save_token_to_cache({})
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
                logger.info(f"[API Call] Query for NEXT recently played.")
            else:
                # If there were no "next" in response, then just stop the while loop
                querying_new_songs = False
