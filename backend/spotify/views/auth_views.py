from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheFileHandler
from dotenv import load_dotenv
import os
from django.conf import settings


class BaseAuthView(APIView):
    load_dotenv()
    cache_path = os.path.join(settings.BASE_DIR, "spotify", ".auth-cache")
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            cache_handler=CacheFileHandler(cache_path),
            scope="user-read-recently-played",
        ),
    )


class AuthURLView(BaseAuthView):
    def get(self, request):
        url = self.sp.auth_manager.get_authorize_url()
        return Response({"Please Sign In": url})


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
