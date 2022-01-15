from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pytz
import json
from ..models import Tracks, UserActivity
from ..serializers.insert_serializers import (
    TrackEntrySerializer,
    HistoryFileSerializer,
    HistoryEntrySerializer,
)
from ..helpers.helpers import search_spotify_song, insert_user_activity
from .auth_views import BaseAuthView

# Dev only
from dotenv import load_dotenv


class TrackEntryView(APIView):
    def post(self, request):
        serializer = TrackEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"Success": "Track added to database"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImportStreamingHistoryView(APIView):
    def post(self, request):

        serializer = HistoryFileSerializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        # Load environment variable
        load_dotenv()
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

        # Accepts multiple streaming history files
        file_list = request.data.getlist("file")
        data_list = []

        try:
            for file in file_list:
                data_list.extend(json.loads(file.read()).copy())
        except Exception as e:
            raise ValidationError(f"Invalid Streaming History JSON file; {e}")

        for data in data_list:
            history_entry_serializer = HistoryEntrySerializer(data=data)

            # If not valid for some reason, just continue to next iteration
            if not history_entry_serializer.is_valid():
                continue

            # Won't let duplicates be added into Streaming History
            history_entry_serializer.save()

            track_name = data.get("trackName")
            artist_name = data.get("artistName")
            end_time = data.get("endTime")
            ms_played = data.get("msPlayed")

            # Neeed to calculate 'played_at' if I want to add to UserActivity
            end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
            played_at = end_time_dt - timedelta(milliseconds=ms_played)
            # Pass it to UTC
            played_at = played_at.replace(tzinfo=pytz.UTC)

            tracks = Tracks.objects.filter(name=track_name, artists__name=artist_name)
            # If track was already in the database, just add to UserActivity
            if tracks.exists():
                track = tracks.first()

                # Will check if not already in UserActivity
                insert_user_activity(
                    track=track,
                    played_at=played_at,
                    ms_played=ms_played,
                    from_import=True,
                )
            # If not, search it on Spotify, and get all necessary data to send it to TrackEntrySerializer
            # which will also add it to user activity.
            else:
                # Searching song name and artist in spotify to get all the info needed.
                track_resp = search_spotify_song(sp, track_name, artist_name, "track")

                # If not found song on spotify, continue to next iteration
                if not track_resp:
                    continue

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

                # This adds complete info to tracks/albums/etc...
                # But also saves to UserActivity!
                track_entry_serializer = TrackEntrySerializer(data=track_entry_data)
                if track_entry_serializer.is_valid():
                    track_entry_serializer.save()

        return Response(
            {"Success": "History added to database"}, status=status.HTTP_201_CREATED
        )


class RecentlyPlayedView(BaseAuthView):
    """
    This view servers just a way of calling the get_recently_played method.

    Done this way to properly inherit from BaseAuthView.
    """

    def insert_recently_played(self):
        """
        Requests and loops through all recently played song not before added to UserActivity.
        For new songs, send it to TrackEntrySerializer, where all data needed will be requested and then stored to UserActivity
        """

        recently_played = self.sp.current_user_recently_played(limit=50)
        querying_new_songs = True

        while querying_new_songs:
            # Items come ordered from most recent to oldest
            for item in recently_played["items"]:
                track = item.get("track")
                played_at = item.get("played_at")
                track_sp_id = track.get("id")

                # Check if there is already an exact entry for this song on the database
                if UserActivity.objects.filter(
                    track__sp_id=track_sp_id, played_at=played_at
                ).exists():
                    # # If there is, just BREAK THE LOOP.
                    # # Because if this entry was already added, all the following (older) will be already added in the db.
                    # # Also sets querying_new_songs to False, so the while loop will stop.
                    # querying_new_songs = False
                    # break
                    # TODO: See how i'm gonna use this in the future. If i'll break to not query older songs, or I will just continue
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
                    serializer.save()

            # If it got here without "query_new_songs" being set to False, it means that there are more songs to be queried
            if recently_played["next"]:
                # PS: This seems to not work. Spotify seems to always return an empty list
                # So queries next page of songs, and start looping again
                recently_played = self.sp.next(recently_played)
            else:
                # If there were no "next" in response, then just stop the while loop
                querying_new_songs = False
