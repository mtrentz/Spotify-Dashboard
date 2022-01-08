from rest_framework.views import APIView
from ..models import *
from ..serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import pytz
from ..helpers.helpers import search_spotify_song, insert_user_activity


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
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

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
                print("yo")
                continue

            # Won't let duplicates be added into Streaming History
            history_entry_serializer.save()

            # TODO: Talvez pegar uma estatistica tipo "x tracks adicionadas... x ja existentes, etc..."

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
