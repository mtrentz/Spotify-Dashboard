from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheFileHandler
from dotenv import load_dotenv
from django.conf import settings
import os
from .auth_views import BaseAuthView


class RecentlyPlayedView(BaseAuthView):
    def get(self, request):
        tracks = self.sp.current_user_recently_played(limit=2)
        return Response(tracks)
