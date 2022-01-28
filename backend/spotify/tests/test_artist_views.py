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

    def test_top_played_single_track_long_period(self):
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

    def test_top_played_track_with_two_artists(self):
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

    def test_top_played_cals(self):
        """
        Add some mock entries, check if its properly ordering artists,
        if its grouping them together and summing everything properly.
        """
        track_one = Tracks.objects.get(name="Be Yourself")  # Audioslave
        track_two = Tracks.objects.get(name="I Am the Highway")  # Audioslave
        track_three = Tracks.objects.get(name="Telegraph Road")  # Dire Straits

        # Track one will be scattered over the past three days
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
            # Two days ago, 1 entry, 2 minutes
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=2)
                ).isoformat(),
                "ms_played": 120000,
            },
            # One day ago, 1 entry, 2 minutes
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1)
                ).isoformat(),
                "ms_played": 120000,
            },
        ]

        # Tracks two will be only played 5 days ago, 1 entry, 5 min
        entries_two = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=5)
                ).isoformat(),
                "ms_played": 300000,
            }
        ]

        # Track three will have been played 2 weeks ago, and not show on calcs
        entries_three = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=14)
                ).isoformat(),
                "ms_played": 120000,
            }
        ]

        # Insert them
        self.insert_track_entries(track_one, entries_one)
        self.insert_track_entries(track_two, entries_two)
        self.insert_track_entries(track_three, entries_three)

        # Checking if the top played artists are correct
        res = self.client.get(reverse("top_played_artists"), {"days": 7})

        # First, check for response ok
        self.assertEqual(res.status_code, 200)

        # Check if there is only one artists
        self.assertEqual(len(res.json()), 1)

        # Check if the artist is Audioslave
        self.assertEqual(res.json()[0]["artist"], "Audioslave")

        # Request now to include the ones 14 days ago
        res = self.client.get(reverse("top_played_artists"), {"days": 20})

        # First, check for response ok
        self.assertEqual(res.status_code, 200)

        # Check if now there are 2 artists
        self.assertEqual(len(res.json()), 2)

        # Check if the most played is still audioslave
        self.assertEqual(res.json()[0]["artist"], "Audioslave")

        # Check if the second one is Dire Straits
        self.assertEqual(res.json()[1]["artist"], "Dire Straits")

    def test_unique_artists_query_params(self):
        """
        Check if the query params are working properly
        """
        # Check if long days (period) is allowed
        res = self.client.get(reverse("unique_artists"), {"days": 1200})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 0)
        # Growth should be 0 since there are no tracks
        self.assertEqual(res.json()["growth"], 0)

        # Check if negative days raises error
        res = self.client.get(reverse("unique_artists"), {"days": -1})
        self.assertEqual(res.status_code, 400)

        # Check if 0 days returns empty
        res = self.client.get(reverse("unique_artists"), {"days": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 0)
        self.assertEqual(res.json()["growth"], 0)

        # Check if strings raises error
        res = self.client.get(reverse("unique_artists"), {"days": "a"})
        self.assertEqual(res.status_code, 400)

    def test_unique_artists_calcs(self):
        """
        Checking if the artist count and growth is correct.

        Remembering that to be considered in this view tracks has to be
        listened to for at least 2 mins
        """
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
        res = self.client.get(reverse("unique_artists"), {"days": 7})

        # Response ok
        self.assertEqual(res.status_code, 200)

        # Count should be one, since its only for the current period
        self.assertEqual(res.json()["count"], 1)

        # At the moment, there was 2 artists played last week and one this week
        # so the growth has to be -50%
        self.assertEqual(res.json()["growth"], -0.5)

        # Now I'll add another artist to be played this week, so the growth is 0
        new_entry = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=3)
                ).isoformat(),
                "ms_played": 300000,
            }
        ]

        self.insert_track_entries(track_three, new_entry)

        res = self.client.get(reverse("unique_artists"), {"days": 7})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["growth"], 0)
