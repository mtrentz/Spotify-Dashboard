from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheFileHandler
from dotenv import load_dotenv
from spotify.models import SpotifyAuthorizationTokens
import os
from django.conf import settings


class AuthURLView(APIView):
    load_dotenv()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-recently-played"))

    url = sp.auth_manager.get_authorize_url()

    def get(self, request):
        return Response({"Please Sign In": self.url})


class AuthTokenView(APIView):
    load_dotenv()
    cache_path = os.path.join(settings.BASE_DIR, "spotify", ".auth-cache")
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            cache_handler=CacheFileHandler(cache_path),
            scope="user-read-recently-played",
        ),
    )

    def post(self, request):
        try:
            # Get code from params
            code = request.data.get("code")
            # Get access token
            token_info = self.sp.auth_manager.get_access_token(code)
            # Save it to file cache
            self.sp.auth_manager.cache_handler.save_token_to_cache(token_info)
        except Exception as e:
            return Response({"Error": {f"Error storing tokens {e}"}})
        # Don't return the tokens since the user (browser) shouldnt't have access to it
        return Response({"Success": "Tokens stored"})
