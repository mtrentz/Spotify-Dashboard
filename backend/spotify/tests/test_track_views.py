from rest_framework.test import APITestCase
from django.urls import reverse
from spotify.tasks import insert_track_entry
from spotify.models import Tracks
from datetime import datetime, timedelta, timezone


class TestTrackViews(APITestCase):
    """
    Here I will be inserting user activity entries and
    test if the views are responding correctly.

    Check fixtures or test_insert docstring to know about the data already
    in the database.

    Don't try to get different tracks to prevent API Calls.
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
        res = self.client.get(reverse("top_played_tracks"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_top_played_query_params(self):
        """
        Just make sure if the qty and days parameters are working as intended
        """
        # Check if long days (period) is allowed
        res = self.client.get(reverse("top_played_tracks"), {"days": 1200})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 0)

        # Check if negative days raises error
        res = self.client.get(reverse("top_played_tracks"), {"days": -1})
        self.assertEqual(res.status_code, 400)

        # Check if 0 days returns empty
        res = self.client.get(reverse("top_played_tracks"), {"days": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 0)

        # Check for negative qty
        res = self.client.get(reverse("top_played_tracks"), {"qty": -1})
        self.assertEqual(res.status_code, 400)

        # Check for 0 qty
        res = self.client.get(reverse("top_played_tracks"), {"qty": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 0)

    def test_single_track_long_period(self):
        """
        Add single track, check if returns as top.
        """
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

        res = self.client.get(reverse("top_played_tracks"))

        # Check if response was ok and it returned only one track
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # Check if is returning the correct track name, album name
        # artist and minutes played
        self.assertEqual(res.json()[0]["track"], track.name)
        self.assertEqual(res.json()[0]["album"], track.album.name)
        # Artists is a list
        self.assertEqual(res.json()[0]["artists"][0], track.artists.all()[0].name)
        self.assertEqual(res.json()[0]["minutes_played"], 2)

        # Just making sure, try passing a 'days' parameter
        # and check if everything is still the same
        res = self.client.get(reverse("top_played_tracks"), {"days": 500})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

    def test_top_played_calcs(self):
        """
        Add some mock entries, check if its properly ordering tracks,
        if its grouping them together and summing everything properly.
        """
        track_one = Tracks.objects.get(name="Be Yourself")
        track_two = Tracks.objects.get(name="I Am the Highway")
        track_three = Tracks.objects.get(name="Telegraph Road")

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

        # Checking if the top played tracks are correct
        res = self.client.get(reverse("top_played_tracks"), {"days": 7})

        # First, check for response ok
        self.assertEqual(res.status_code, 200)

        # Now check if there are only two tracks, since track three
        # was 2 weeks ago
        self.assertEqual(len(res.json()), 2)

        # Check if the tracks are ordered correctly
        # First one should've been the one most played
        self.assertGreater(
            res.json()[0]["minutes_played"], res.json()[1]["minutes_played"]
        )

        # The top one should've been played for 10 minutes total
        self.assertEqual(res.json()[0]["minutes_played"], 10)
        # Second one should've been played for 5 minutes total
        self.assertEqual(res.json()[1]["minutes_played"], 5)

    def test_unique_tracks_query_params(self):
        """
        Check if the query params are working properly
        """
        # Check if long days (period) is allowed
        res = self.client.get(reverse("unique_tracks"), {"days": 1200})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 0)
        # Growth should be 0 since there are no tracks
        self.assertEqual(res.json()["growth"], 0)

        # Check if negative days raises error
        res = self.client.get(reverse("unique_tracks"), {"days": -1})
        self.assertEqual(res.status_code, 400)

        # Check if 0 days returns empty
        res = self.client.get(reverse("unique_tracks"), {"days": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 0)
        self.assertEqual(res.json()["growth"], 0)

        # Check if strings raises error
        res = self.client.get(reverse("unique_tracks"), {"days": "a"})
        self.assertEqual(res.status_code, 400)

    def test_unique_tracks_calc(self):
        """
        Checking if the track count and growth is correct.

        Remembering that to be considered in this view tracks has to be
        listened to for at least 2 mins
        """
        track_one = Tracks.objects.get(name="Be Yourself")
        track_two = Tracks.objects.get(name="I Am the Highway")
        track_three = Tracks.objects.get(name="Telegraph Road")

        # Played this week and a bit last week
        entries_one = [
            # Played for 10 min yesterday
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=1)
                ).isoformat(),
                "ms_played": 600000,
            },
            # Played for 5 min last week, 10 days ago
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=10)
                ).isoformat(),
                "ms_played": 300000,
            },
        ]

        # Played a bit this week and last week
        entries_two = [
            # Two days ago, played for 5 min
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=2)
                ).isoformat(),
                "ms_played": 300000,
            },
            # Played for 5 min last week, 10 days ago
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=10)
                ).isoformat(),
                "ms_played": 300000,
            },
        ]

        # Track three will be played only last week
        entries_three = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=10)
                ).isoformat(),
                "ms_played": 600000,
            }
        ]

        # Insert them
        self.insert_track_entries(track_one, entries_one)
        self.insert_track_entries(track_two, entries_two)
        self.insert_track_entries(track_three, entries_three)

        # Now check for the response in the last 7 days
        res = self.client.get(reverse("unique_tracks"), {"days": 7})

        # Response ok
        self.assertEqual(res.status_code, 200)

        # Count should be two, since its only for the current period
        self.assertEqual(res.json()["count"], 2)

        # Growth should be -33 % since last week I've listened to three tracks
        # and this week i've listened to two
        self.assertEqual(res.json()["growth"], -1 / 3)

        # Now I'll add a track to be played this week, so the growth should be 0
        new_entry = [
            {
                "played_at": (
                    datetime.now(timezone.utc) - timedelta(days=3)
                ).isoformat(),
                "ms_played": 300000,
            }
        ]
        self.insert_track_entries(track_three, new_entry)

        # Check if the growth is 0
        res = self.client.get(reverse("unique_tracks"), {"days": 7})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["growth"], 0)

        # Change the days to 14, should be 3 tracks and 0 count
        # just because there wasnt a previous period to compare to
        res = self.client.get(reverse("unique_tracks"), {"days": 14})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 3)
        self.assertEqual(res.json()["growth"], 0)
