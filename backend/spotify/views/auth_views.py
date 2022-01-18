from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheFileHandler
import os

# Dev only
from dotenv import load_dotenv


class BaseAuthView(APIView):
    load_dotenv()
    cache_path = os.path.join(settings.BASE_DIR, "spotify", ".auth-cache")
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            cache_handler=CacheFileHandler(cache_path),
            scope="user-read-recently-played",
            show_dialog=True,
        ),
    )


class AuthURLView(BaseAuthView):
    def get(self, request):
        url = self.sp.auth_manager.get_authorize_url()
        return Response({"url": url})


class AuthTokenView(BaseAuthView):
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
