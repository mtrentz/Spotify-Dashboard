from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


class TrackEntryView(APIView):
    def post(self, request):
        serializer = TrackEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # TODO: Responder só um "ok" ou algo assim, nao precisa dos dados.
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImportStreamingHistoryView(APIView):
    def post(self, request):
        serializer = HistoryFileSerializer(data=request.data)
        if serializer.is_valid():

            # Load environment variable
            load_dotenv()
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

            # List of objects containing the play history
            data_list = request.data.get("file").read()
            try:
                data_list = json.loads(data_list)
            except Exception as e:
                return ValidationError("Invalid Streaming History JSON file")

            for data in data_list:
                history_entry_serializer = HistoryEntrySerializer(data=data)
                if history_entry_serializer.is_valid():

                    # Won't add duplicates into Streaming History
                    history_entry_serializer.save()

                    # TODO: Talvez pegar uma estatistica tipo "x tracks adicionadas... x ja existentes, etc..."

                    track_name = data.get("trackName")
                    artist_name = data.get("artistName")
                    end_time = data.get("endTime")
                    ms_played = data.get("msPlayed")

                    print(f"{track_name} - {artist_name}")

                    # Neeed to calculate 'played_at' if I want to add to UserActivity (By sending to TrackEntryView)
                    end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                    played_at = end_time_dt - timedelta(milliseconds=ms_played)

                    # Removes "Remaster" or "Live" from track name to search it.
                    if "Remaster" in track_name or "Live" in track_name:
                        track_name = track_name.split(" - ")[0]

                    # TODO: Colocar um check aqui pra nao fazer request se a musica já tem com mesmo autor, nome no Tracks

                    tracks = Tracks.objects.filter(
                        name=track_name, artist__name=artist_name
                    )
                    # If track was already in the database, just add to UserActivity
                    if tracks.exists():
                        track = tracks.first()
                        user_activity, _ = UserActivity.objects.get_or_create(
                            track=track,
                            played_at=played_at,
                            ms_played=ms_played,
                            from_import=True,
                        )
                        user_activity.save()
                    # If not, search it on Spotify, and get all necessary data to send it to TrackEntrySerializer
                    # which will also add it to user activity.
                    else:
                        # Searching song name and artist in spotify to get all the info needed.
                        track = sp.search(
                            q=f"track:{track_name} artist:{artist_name}",
                            type="track",
                            limit=1,
                        )
                        track_resp = track["tracks"]["items"][0]

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

                        track_entry_serializer = TrackEntrySerializer(
                            data=track_entry_data
                        )
                        # This adds complete info to tracks/albums/etc...
                        # But also saves to UserActivity!
                        if track_entry_serializer.is_valid():
                            track_entry_serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
