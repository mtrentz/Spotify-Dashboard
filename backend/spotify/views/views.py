from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheFileHandler
from dotenv import load_dotenv
from spotify.models import SpotifyAuthorizationTokens
from django.conf import settings
import os


class RecentlyPlayedView(APIView):
    load_dotenv()
    cache_path = os.path.join(settings.BASE_DIR, "spotify", ".auth-cache")
    # sp = spotipy.Spotify(
    #     auth_manager=SpotifyOAuth(cache_handler=CacheFileHandler(cache_path)),
    # )

    def get(self, request):
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(cache_handler=CacheFileHandler(self.cache_path)),
        )
        # cache = sp.auth_manager.cache_handler.get_cached_token()
        # print(cache)
        # print(request.session.get("token_info"))
        # cache = DjangoSessionCacheHandler(request)
        # token = cache.get_cached_token()
        # print(token)
        print(sp.auth_manager.cache_handler.get_cached_token())

        tracks = sp.current_user_recently_played(limit=2)
        # print(tracks)
        return Response(tracks)
        # return Response({"Success": "Got top tracks"})
