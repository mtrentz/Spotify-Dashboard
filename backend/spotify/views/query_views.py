from rest_framework.response import Response
from dotenv import load_dotenv
from django.conf import settings
from .auth_views import BaseAuthView
from ..models import UserActivity
from ..serializers import TrackEntrySerializer

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
            # Items come ordered from most recent to oldest
            for item in recently_played["items"]:
                track = item.get("track")
                played_at = item.get("played_at")
                track_sp_id = track.get("id")

                print(f"{played_at} - {track.get('name')}")

                # Check if there is already an exact entry for this song on the database
                if UserActivity.objects.filter(
                    track__sp_id=track_sp_id, played_at=played_at
                ).exists():
                    # If there is, just BREAK THE LOOP.
                    # Because if this entry was already added, all the following (older) will be already added in the db.
                    # Also sets querying_new_songs to False, so the while loop will stop.
                    # querying_new_songs = False
                    # break
                    # TODO: See how i'm gonna use this in the future. If i'll break to not query older songs, or I will just continue
                    continue

                # Get the list of artists
                artists = track.get("artists")
                # Get all artists ids
                artists_sp_ids = [artist.get("id") for artist in artists]

                track_entry_data = {
                    "album_sp_id": track.get("album").get("id"),
                    "artists_sp_ids": artists_sp_ids,
                    "track_sp_id": track_sp_id,
                    "track_name": track.get("name"),
                    "track_duration": track.get("duration_ms"),
                    "track_popularity": track.get("popularity"),
                    "track_explicit": track.get("explicit"),
                    "track_number": track.get("track_number"),
                    "track_disc_number": track.get("disc_number"),
                    "track_type": track.get("type"),
                    "played_at": played_at,
                    # Tracks that come from Recently Played were always listened to fully.
                    "ms_played": track.get("duration_ms"),
                    "from_import": False,
                }
                serializer = TrackEntrySerializer(data=track_entry_data)
                if serializer.is_valid():
                    serializer.save()
            # If it got here without "query_new_songs" being set to False, it means that there are more songs to be queried
            if recently_played["next"]:
                # PS: This seems to not work. Spotify seems to always return an empty list
                # So queries next page of songs, and start looping again
                recently_played = self.sp.next(recently_played)
            else:
                # If there were no "next" in response, then just stop the while loop
                querying_new_songs = False
