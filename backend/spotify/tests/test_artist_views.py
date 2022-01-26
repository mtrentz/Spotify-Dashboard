from rest_framework.test import APITestCase
from django.urls import reverse
from spotify.tasks import insert_track_entry
from spotify.models import Tracks, Artists
from datetime import datetime, timedelta, timezone


class TestTrackViews(APITestCase):
    """
    I'll be testing the artist views, which give stats for
    unique, most played artists in some period.

    For this, I'll be needed to add entries to user activity.

    To make this easy, i'll be using the tracks/albums/artists from the
    fixtures.

    Avoid using any other tracks other than this to avoid API Calls.
    """

    fixtures = ["albums.json", "artists.json", "genres.json", "tracks.json"]

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

    def test_empty_top_played(self):
        res = self.client.get(reverse("top_played_artists"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_top_played_query_params(self):
        """
        Just make sure if the qty and days parameters are working as intended
        """
        # Check if long days (period) is allowed
        res = self.client.get(reverse("top_played_artists"), {"days": 1200})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 0)

        # Check if negative days raises error
        res = self.client.get(reverse("top_played_artists"), {"days": -1})
        self.assertEqual(res.status_code, 400)

        # Check if 0 days returns empty
        res = self.client.get(reverse("top_played_artists"), {"days": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 0)

        # Check for negative qty
        res = self.client.get(reverse("top_played_artists"), {"qty": -1})
        self.assertEqual(res.status_code, 400)

        # Check for 0 qty
        res = self.client.get(reverse("top_played_artists"), {"qty": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 0)

    def test_single_track_long_period(self):
        """
        Add single track of a single artist.
        """
        # Artist = Audioslave
        track = Tracks.objects.get(name="Be Yourself")
        entries = [
            # Add one track yesterday
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1)
                ).isoformat(),
                "ms_played": 120000,
            }
        ]
        # Add the single entry
        self.insert_track_entries(track, entries)

        res = self.client.get(reverse("top_played_artists"))

        # Check if response was ok and it returned only one artist
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # Check if is returning the correct track name, album name
        # artist and minutes played
        self.assertEqual(res.json()[0]["artist"], track.artists.all()[0].name)
        self.assertEqual(res.json()[0]["minutes_played"], 2)

        # Just making sure, try passing a 'days' parameter
        # and check if everything is still the same
        res = self.client.get(reverse("top_played_artists"), {"days": 500})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

    def test_track_with_two_artists(self):
        """
        Some tracks have two artists. Unfortunately in the fixture I don't have
        any like this. So I'll just edit the database.
        """
        # The original artist on this one is Dire Straits
        track = Tracks.objects.get(name="Telegraph Road")
        new_artist = Artists.objects.get(name="Audioslave")

        # Add the new artist to the track
        track.artists.add(new_artist)

        # Retrieve from DB to check if has two artists
        track_one = Tracks.objects.get(name="Telegraph Road")
        self.assertEqual(len(track.artists.all()), 2)

        # Now add some entries for this track with two artists.
        entries_one = [
            # Yesterday, three times, two minutes each
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1)
                ).isoformat(),
                "ms_played": 120000,
            },
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1, hours=10)
                ).isoformat(),
                "ms_played": 120000,
            },
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1, hours=5)
                ).isoformat(),
                "ms_played": 120000,
            },
        ]

        # Single entry for a track that has only one artist (Audioslave)
        # Played yesterday for 5 min
        track_two = Tracks.objects.get(name="Be Yourself")
        entries_two = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1)
                ).isoformat(),
                "ms_played": 300000,
            }
        ]

        # Insert the entries
        self.insert_track_entries(track_one, entries_one)
        self.insert_track_entries(track_two, entries_two)

        # Query the view
        res = self.client.get(reverse("top_played_artists"), {"days": 7})
        # First check if the response is ok
        self.assertEqual(res.status_code, 200)
        # Check if it returned two artists
        self.assertEqual(len(res.json()), 2)

        # Now check if the times are properly added.
        # Audioslave should have 5 + 2 + 2 + 2 minutes
        # Dire Straits should have 2 + 2 + 2 minutes
        # Also, the endpoint returns a list, so the first one should be
        # Audioslave, since it was the one most listened to
        self.assertEqual(res.json()[0]["artist"], "Audioslave")
        self.assertEqual(res.json()[0]["minutes_played"], 11)

        # Check for second
        self.assertEqual(res.json()[1]["artist"], "Dire Straits")
        self.assertEqual(res.json()[1]["minutes_played"], 6)
