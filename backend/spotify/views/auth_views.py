from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


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
        # print(request.data)
        code = request.data.get("code")
        token = self.sp.auth_manager.get_access_token(code)
        print(token)
        return Response({"Token": token})
