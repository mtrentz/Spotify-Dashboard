from rest_framework.test import APITestCase
from django.urls import reverse
from spotify.tasks import insert_track_entry
from spotify.models import Tracks
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User


class TestAlbumViews(APITestCase):
    """
    I'll be testing the views for albums here.

    For this, I'll be needed to add entries to user activity.

    To make this easy, i'll be using the tracks/albums/artists from the
    fixtures.

    Avoid using any other tracks other than this to avoid API Calls.
    """

    fixtures = ["albums.json", "artists.json", "genres.json", "tracks.json"]

    def setUp(self):
        user = User.objects.create_superuser('admin', 'admin@admin.com', "admin")
        self.client.force_authenticate(user)

    @staticmethod
    def insert_track_entries(track, entries):
        """
        This is going to insert one or more entries of the same track.

        Entries are expected as list of objects with time played (string) and ms_played (int).
        [
            {
                "played_at": "2020-01-01T00:00:00.000Z",
                "ms_played": 12345,
            },
            ...
        ]
        """
        track_data = {
            "album_sp_id": track.album.sp_id,
            "artists_sp_ids": [a.sp_id for a in track.artists.all()],
            "track_sp_id": track.sp_id,
            "track_name": track.name,
            "track_duration": track.duration,
            "track_popularity": track.popularity,
            "track_explicit": track.explicit,
            "track_number": track.track_number,
            "track_disc_number": track.disc_number,
            "track_type": track.type,
            "from_import": False,
        }

        for entry in entries:
            track_data["played_at"] = entry["played_at"]
            track_data["ms_played"] = entry["ms_played"]
            insert_track_entry(track_data)

    def test_unique_album_query_params(self):
        # Check if long days (period) is allowed
        res = self.client.get(reverse("unique_albums"), {"days": 1200})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 0)
        # Growth should be 0 since there are no tracks
        self.assertEqual(res.json()["growth"], 0)

        # Check if negative days raises error
        res = self.client.get(reverse("unique_albums"), {"days": -1})
        self.assertEqual(res.status_code, 400)

        # Check if 0 days returns empty
        res = self.client.get(reverse("unique_albums"), {"days": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 0)
        self.assertEqual(res.json()["growth"], 0)

        # Check if strings raises error
        res = self.client.get(reverse("unique_albums"), {"days": "a"})
        self.assertEqual(res.status_code, 400)

    def test_unique_artists_calcs(self):
        """
        Checking if the artist count and growth is correct.

        Remembering that to be considered in this view tracks has to be
        listened to for at least 2 mins
        """
        # Each track is from a different album
        track_one = Tracks.objects.get(name="Be Yourself")
        track_two = Tracks.objects.get(name="I Am the Highway")
        track_three = Tracks.objects.get(name="Telegraph Road")

        # Played this week and a bit last week
        entries_one = [
            # Played for 10 min 10 days ago
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=10)
                ).isoformat(),
                "ms_played": 600000,
            },
        ]

        # Played 5 minutes yesterday
        entries_two = [
            # Two days ago, played for 5 min
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1)
                ).isoformat(),
                "ms_played": 300000,
            },
        ]

        # Played 15 last week
        entries_three = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=10)
                ).isoformat(),
                "ms_played": 900000,
            }
        ]

        # Insert them
        self.insert_track_entries(track_one, entries_one)
        self.insert_track_entries(track_two, entries_two)
        self.insert_track_entries(track_three, entries_three)

        # Now check for the response in the last 7 days
        res = self.client.get(reverse("unique_albums"), {"days": 7})

        # Response ok
        self.assertEqual(res.status_code, 200)

        # Count should be one, since its only for the current period
        self.assertEqual(res.json()["count"], 1)

        # At the moment, there was 2 albums played last week and one this week
        # so the growth has to be -50%
        self.assertEqual(res.json()["growth"], -0.5)

        # Now I'll add another album to be played this week, so the growth is 0
        new_entry = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=3)
                ).isoformat(),
                "ms_played": 300000,
            }
        ]

        self.insert_track_entries(track_three, new_entry)

        res = self.client.get(reverse("unique_albums"), {"days": 7})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["growth"], 0)
