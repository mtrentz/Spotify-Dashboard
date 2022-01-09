from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheFileHandler
from dotenv import load_dotenv
from django.conf import settings
import os


class RecentlyPlayedView(APIView):
    load_dotenv()
    cache_path = os.path.join(settings.BASE_DIR, "spotify", ".auth-cache")

    def get(self, request):
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(cache_handler=CacheFileHandler(self.cache_path)),
        )

        tracks = sp.current_user_recently_played(limit=2)
        return Response(tracks)
