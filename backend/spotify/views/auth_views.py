from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


class AuthView(APIView):
    load_dotenv()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

    url = sp.auth_manager.get_authorize_url()

    def get(self, request):

        return Response({"Please Sign In": self.url})
