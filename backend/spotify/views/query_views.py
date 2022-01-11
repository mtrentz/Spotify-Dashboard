from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheFileHandler
from dotenv import load_dotenv
from django.conf import settings
import os
from .auth_views import BaseAuthView

# TODO: Tirar limite e ver como lidar com o CURSOR depois pra poder fazer a pagination
class RecentlyPlayedView(BaseAuthView):
    def get(self, request):
        limit = request.data.get("limit", 50)
        after = request.data.get("after", None)
        before = request.data.get("before", None)
        try:
            tracks = self.sp.current_user_recently_played(
                limit=limit, after=after, before=before
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        return Response(tracks)

    def insert_recently_played(self):
        """
        Requests and loops through all recently played song not before added to UserActivity.
        For new songs, send it to TrackEntrySerializer, where all data needed will be requested and then stored to UserActivity
        """

        recently_played = self.sp.current_user_recently_played(limit=50)
        querying_new_songs = True

        while querying_new_songs:
            for item in recently_played["items"]:
                # if not UserActivity.objects.filter(track_id=item['track']['id']).exists():
                #     serializer = TrackEntrySerializer(data=item)
                #     if serializer.is_valid():
                #         serializer.save()
                pass
            if recently_played["next"]:
                recently_played = self.sp.next(recently_played)
            else:
                querying_new_songs = False
