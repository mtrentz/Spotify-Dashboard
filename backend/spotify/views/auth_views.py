from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from spotify.models import SpotifyAuthorizationTokens


class AuthURLView(APIView):
    load_dotenv()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

    url = sp.auth_manager.get_authorize_url()

    def get(self, request):

        return Response({"Please Sign In": self.url})


class AuthTokenView(APIView):
    load_dotenv()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    print("Got in Auth token view")

    def post(self, request):
        try:
            code = request.data.get("code")
            token = self.sp.auth_manager.get_access_token(code)
            # TODO: not 100% sure this is the right way to do this
            SpotifyAuthorizationTokens.objects.update_or_create(
                access_token=token["access_token"],
                refresh_token=token["refresh_token"],
                expires_in=token["expires_in"],
                expires_at=token["expires_at"],
                scope=token["scope"],
                token_type=token["token_type"],
            )
        except Exception as e:
            return Response({"Error": {f"Error storing tokens {e}"}})
        # Don't return the tokens since the user (browser) shouldnt't have access to it
        return Response({"Success": "Tokens stored"})
