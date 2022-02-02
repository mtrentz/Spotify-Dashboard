from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.test.utils import tag
from django.db.models import Sum
from spotify.models import Albums, Artists, Tracks, Genres, UserActivity
from spotify.tasks import insert_track_batch_from_history, insert_track_entry
from spotify.helpers import insert_user_activity
from django.test import override_settings
import json
from django.urls import reverse
import io
from unittest import mock
import os


class TestInsert(APITestCase):
    """
    Here i'm going to be testing the logic to insert USER ACTIVITY into the database.

    Inserting artists/tracks/albums/genres into the DB requires API calls to Spotify. So i'll refrain from doing that,
    since it's too much of a hassle to mock the API calls.

    When trying to insert UserActivity/History this app checks if the tracks, albums, artists, genres already exist in the DB,
    and if so, it will not request them from Spotify API.

    As of right now in the fixture I added two artists, three tracks, three albums and a few genres.

    Artists: Audioslave, Dire Straits.
    Tracks: Audioslave - Be Yourself, Audioslave - I Am the Highway, Dire Straits - Telegraph Road.
    Albums: Audioslave - Audioslave, Audioslave - Out of Exile, Dire Straits - Love Over Gold.
    Genres (some): rock, classic rock, nu metal, alternative rock.

    Caution: If other fixtures are needed for testing, make sure to name them differently and not
    change anything with these existing ones, since the tests are very specific for this data.
    """

    fixtures = ["albums.json", "artists.json", "genres.json", "tracks.json"]

    def setUp(self):
        """
        Creates a mock history from spotify. Adds it to the database.
        """
        user = User.objects.create_superuser('admin', 'admin@admin.com', "admin")
        self.client.force_authenticate(user)

        # This is a mock history data of spotify, using only the artists/tracks shown above.
        # Caution: I'll make some very specific mentions to this data,
        # so never change order, values, etc...
        self.history_data = [
            {
                "end_time": "2021-01-01 23:54",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 10000,
            },
            {
                "end_time": "2021-02-01 11:11",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 20000,
            },
            {
                "end_time": "2021-03-01 12:00",
                "artist_name": "Dire Straits",
                "track_name": "Telegraph Road",
                "ms_played": 30000,
            },
            {
                "end_time": "2021-03-01 13:00",
                "artist_name": "Dire Straits",
                "track_name": "Telegraph Road",
                "ms_played": 30000,
            },
            {
                "end_time": "2021-04-01 13:00",
                "artist_name": "Audioslave",
                "track_name": "I Am the Highway",
                "ms_played": 40000,
            },
            {
                "end_time": "2022-01-01 08:31",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 10000,
            },
        ]

        # Insert it into the database
        insert_track_batch_from_history(self.history_data)

    @tag("skip_setup")
    def test_fixture_load(self):
        """
        Just checking if all fixtures loaded properly
        """
        self.assertEqual(Artists.objects.all().count(), 2)
        self.assertEqual(Albums.objects.all().count(), 3)
        self.assertEqual(Tracks.objects.all().count(), 3)
        self.assertEqual(Genres.objects.all().count(), 11)

    def test_over_insert(self):
        """
        Makes sure that after the set up the only tracks in the DB are the ones from the fixture.
        If this fails is because the API made some external calls to Spotify, which means checking for
        existing tracks/artists in the DB is failing somehow.
        """
        self.assertEqual(Artists.objects.all().count(), 2)
        self.assertEqual(Albums.objects.all().count(), 3)
        self.assertEqual(Tracks.objects.all().count(), 3)
        self.assertEqual(Genres.objects.all().count(), 11)

    @staticmethod
    def amount_of_entries_that_day(year, month, day, expected_amount):
        """Helper method to check how many entries there was that day"""
        return (
            UserActivity.objects.filter(
                played_at__year=year, played_at__month=month, played_at__day=day
            ).count()
            == expected_amount
        )

    @staticmethod
    def unpack_track_data(track):
        """
        Inserting a track as a entry requires some specific fields as will be shown below.
        Since this is a common task for some of the following tests, I'll create this helper method here.
        """
        data = {
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
        }
        return data

    def test_user_activity_setup(self):
        """
        This will check wether the data inserted on setup is correct.

        Everything should've gone to UserActivity table.
        """
        # Check the amount of entries
        self.assertEqual(UserActivity.objects.all().count(), 6)

        # Check the total time played
        ms_sum = sum([d["ms_played"] for d in self.history_data])
        self.assertEqual(
            UserActivity.objects.all().aggregate(Sum("ms_played"))["ms_played__sum"],
            ms_sum,
        )

        # Check for specific dates
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=1, day=1, expected_amount=1
            )
        )
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=2, day=1, expected_amount=1
            )
        )
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=3, day=1, expected_amount=2
            )
        )
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=4, day=1, expected_amount=1
            )
        )

        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021,
            ).count(),
            5,
        )

        # Check if all tracks were marked as "from_import", which they should
        self.assertEqual(
            UserActivity.objects.filter(from_import=True).count(),
            6,
        )

    def test_insert_history_twice(self):
        """
        Here I'll check that everything will be skipped when adding the same history twice,
        once in the setup, another in this method.

        It's exactly the same tests as the method above.
        """
        # Insert it into the database again
        insert_track_batch_from_history(self.history_data)

        # Check the amount of entries
        self.assertEqual(UserActivity.objects.all().count(), 6)

        # Check the total time played
        ms_sum = sum([d["ms_played"] for d in self.history_data])
        self.assertEqual(
            UserActivity.objects.all().aggregate(Sum("ms_played"))["ms_played__sum"],
            ms_sum,
        )

        # Check for specific dates
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=1, day=1, expected_amount=1
            )
        )

        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=2, day=1, expected_amount=1
            )
        )

        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021,
            ).count(),
            5,
        )

        # Check if all tracks were marked as "from_import", which they should
        self.assertEqual(
            UserActivity.objects.filter(from_import=True).count(),
            6,
        )

    def test_track_entry_insert(self):
        """
        There are two flows for entering data into the database. One is longer and has to SEARCH the spotify api (history),
        and the other already has ID of tracks and more info, then it's just a matter of querying for artist and album id (recently played).

        Here, i'll try inserting a track having directly most of its info. It should be marked as from_import False on UserActivity,
        and be normally added alongside other tracks coming from history.
        """
        # First I'll query the db for a track.
        track = Tracks.objects.get(name="Be Yourself")
        track_data = self.unpack_track_data(track)

        # To add it as a track entry I need a few more info that usually comes
        # when querying the official Spotify API for Recently Played!
        # The date is almost always more accurate, in this pattern:
        track_data["played_at"] = "2021-01-01T10:10:10.562Z"
        track_data["ms_played"] = 111
        track_data["from_import"] = False

        # Now i'll insert it.
        insert_track_entry(track_data)

        # First, just make sure nothing new was added to the DB, since this track should already exist.
        self.assertEqual(Artists.objects.all().count(), 2)
        self.assertEqual(Albums.objects.all().count(), 3)
        self.assertEqual(Tracks.objects.all().count(), 3)
        self.assertEqual(Genres.objects.all().count(), 11)

        # Now, check if there is one entry in UserActivity that is NOT from_import
        self.assertEqual(UserActivity.objects.filter(from_import=False).count(), 1)

        # Then, check if this new entry is SITTING ALONGSIDE with another one
        # from the setUp, on the same day as this
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=1, day=1, expected_amount=2
            )
        )

        # Check if the ms_played is also correct,
        total_ms_day = track_data["ms_played"] + self.history_data[0]["ms_played"]
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=1, played_at__day=1
            ).aggregate(Sum("ms_played"))["ms_played__sum"],
            total_ms_day,
        )

    def test_insert_from_recently_played_when_history_exists(self):
        """
        There is some logic that happens when trying to add user activity that comes from different
        sources (e.g. one comes from RECENTLY PLAYED and the other from HISTORY).

        In the setup I've added some tracks FROM HISTORY, and now I'll try to add a track from RECENTLY PLAYED,
        and check wether my logic is working correctly.
        """

        # Get a track
        track = Tracks.objects.get(name="I Am the Highway")

        # From the SETUP there was a entry of I Am the Highway played at
        # 2021-04-01, with end time of 13:00:00 and was played for 40000 ms.
        # To get the played_at from the end_time I have to subtract the duration.
        # The played_at for this track is: 2021-04-01T12:59:20.000Z
        # The exact same time but formated very accurately
        played_at = "2021-04-01T12:59:20.000Z"
        ms_played = 40001
        from_import = False

        # I'll add this one directly with the function used by insert_track_entry
        insert_user_activity(track, ms_played, played_at, from_import)

        # When a track comes from RECENTLY PLAYED
        # and is very similar to a existing one that was from HISTORY, it will
        # OVERRIDE the existing one, since entries coming from RECENTLY PLAYED are
        # way more accurate.

        # Here I'll check if there is only one track in the DB that day, since it
        # should have been overriden.
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=4, day=1, expected_amount=1
            )
        )

        # I'll also check if the ms_played is 40001 now, instead of 40000. And it's also from_import=False
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=4, played_at__day=1
            ).aggregate(Sum("ms_played"))["ms_played__sum"],
            40001,
        )
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=4, played_at__day=1
            )
            .first()
            .from_import,
            False,
        )

        # The same should still happen even when the played_at
        # are slightly different (up to 1min difference).
        # Here I'll get another track from the SetUp, since the
        # one before is not from_history=False in the db.
        new_track = Tracks.objects.get(name="Telegraph Road")

        # In the setup two entries were added for this song with end_times of
        # 2021-03-01T12:00:00.000Z and 2021-03-01T13:00:00.000Z
        # and ms_played for both of 30000.
        # Thus, the played_at for the first one should be:
        # 2021-03-01T11:59:30.000Z
        # And the second one:
        # 2021-03-01T12:59:30.000Z

        # I'll now add one track 50s before the first one, and then 50s after the second one.
        # Both of them will be overriden.
        new_played_at_first = "2021-03-01T11:58:40.000Z"
        new_ms_played_first = 10000
        new_played_at_second = "2021-03-01T13:00:20.000Z"
        new_ms_played_second = 70000
        insert_user_activity(
            track=new_track,
            ms_played=new_ms_played_first,
            played_at=new_played_at_first,
            from_import=False,
        )
        insert_user_activity(
            track=new_track,
            ms_played=new_ms_played_second,
            played_at=new_played_at_second,
            from_import=False,
        )

        # What I expect is that both of them were overriden, so I'll check if that day has two tracks.
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=3, day=1, expected_amount=2
            )
        )

        # Also, the ms_played now should be 10000+70000
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=3, played_at__day=1
            ).aggregate(Sum("ms_played"))["ms_played__sum"],
            10000 + 70000,
        )

        # Both should be from_import=False, so check if at that day there was none from_import=True
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=3, played_at__day=1
            )
            .filter(from_import=True)
            .count(),
            0,
        )

    def test_insert_from_history_when_recently_played_exists(self):
        """
        Here I'll do the opposite of the last one. I'll first insert a track that simullates being from RECENTLY_PLAYED.

        Then i'll add a new entry thats should be the same entry but from history, to check if the logic is correct.

        If everything is correct, the entry should remain unchanged. Meaning that the entry from history should not be added
        and also even if it has a different ms_played or time_played, the original (from recently_played) should stay unchanged!
        """

        track = Tracks.objects.get(name="Telegraph Road")
        track_data = self.unpack_track_data(track)

        # Here I'll make up some date that IS DIFFERENT FROM ANY IN SET UP
        # so there won't be any confusions.
        track_data["played_at"] = "2020-10-10T08:00:00.000Z"
        track_data["ms_played"] = 12345
        track_data["from_import"] = False

        # Adding it to the database
        insert_track_entry(track_data)

        # Make sure it was added
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=10, expected_amount=1
            )
        )

        # Now I'll add a new entry simulating it from history
        history_entry = {
            "end_time": "2020-10-10 08:00",
            # Different ms_played, has to be less than 1m to be considered equivalent entry
            "ms_played": 123,
            "track_name": "Telegraph Road",
            "artist_name": "Dire Straits",
        }

        # Inserting it to the database
        insert_track_batch_from_history([history_entry])

        # First, make sure there is still only 1 that day
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=10, expected_amount=1
            )
        )

        # Check if the ms_played is equal to the one from recently_played
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2020, played_at__month=10, played_at__day=10
            ).aggregate(Sum("ms_played"))["ms_played__sum"],
            12345,
        )

        # Check if the from_import is False
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2020, played_at__month=10, played_at__day=10
            )
            .first()
            .from_import,
            False,
        )

        # Doing it again but with slightly different time played,
        # running same tests.
        history_entry = {
            "end_time": "2020-10-10 08:01",
            "ms_played": 1,
            "track_name": "Telegraph Road",
            "artist_name": "Dire Straits",
        }
        insert_track_batch_from_history([history_entry])

        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=10, expected_amount=1
            )
        )

        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2020, played_at__month=10, played_at__day=10
            ).aggregate(Sum("ms_played"))["ms_played__sum"],
            12345,
        )

        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2020, played_at__month=10, played_at__day=10
            )
            .first()
            .from_import,
            False,
        )

    def test_add_from_recently_played_twice(self):
        """
        Very simple. Just get a exact track entry from recently_played, add twice the exact same.

        Nothing should be added.
        """
        track = Tracks.objects.get(name="Telegraph Road")
        track_data = self.unpack_track_data(track)

        # Here I'll make up some date that IS DIFFERENT FROM ANY IN SET UP
        # so there won't be any confusions.
        track_data["played_at"] = "2020-11-11T11:11:11.111Z"
        track_data["ms_played"] = 1337
        track_data["from_import"] = False

        insert_track_entry(track_data)
        insert_track_entry(track_data)

        # Check if only one that day
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=11, day=11, expected_amount=1
            )
        )

    def test_add_from_recently_played_twice_slightly_different(self):
        """
        This will test if two entries with very similar played_at, both coming
        from recently played will be added as different.

        It should! Since the logic here is that if for whatever reason
        spotify's API tells me I've listened twice for the same tracks just a few seconds
        apart, then they are different entries.
        """
        track = Tracks.objects.get(name="Telegraph Road")
        track_data = self.unpack_track_data(track)

        # Here I'll make up some date that IS DIFFERENT FROM ANY IN SET UP
        # so there won't be any confusions.
        track_data["played_at"] = "2019-11-11T11:11:11.111Z"
        track_data["ms_played"] = 1337
        track_data["from_import"] = False

        # Inserting it.
        insert_track_entry(track_data)

        # Check if only one that day
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2019, month=11, day=11, expected_amount=1
            )
        )

        # Now change the date very slightly
        track_data["played_at"] = "2019-11-11T11:11:11.112Z"

        # Insert it again
        insert_track_entry(track_data)

        # Check if both are there!
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2019, month=11, day=11, expected_amount=2
            )
        )

    def test_add_from_history_twice_slightly_different(self):
        """
        Just like the one before, if two tracks come from history with very similar time,
        or even the same time and diferent ms_played, it should be added as different since
        its the oficial data!
        """
        history_entry_one = {
            "end_time": "2018-01-01 08:31",
            "artist_name": "Audioslave",
            "track_name": "Be Yourself",
            "ms_played": 10000,
        }
        history_entry_two = {
            "end_time": "2018-01-01 08:32",
            "artist_name": "Audioslave",
            "track_name": "Be Yourself",
            "ms_played": 10000,
        }

        # Inserting it to the database
        insert_track_batch_from_history([history_entry_one, history_entry_two])

        # Check if there are two that day
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2018, month=1, day=1, expected_amount=2
            )
        )

        # Now check adding the exact same time but different ms_played.
        # This situation is not supposed to happen, but the logic is that
        # it should add twice, since there is no reason to doubt the oficial spotify data.
        history_entry_one["ms_played"] = 10001
        insert_track_batch_from_history([history_entry_one])

        # Check if now there's three that day
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2018, month=1, day=1, expected_amount=3
            )
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_insert_single_file(self):
        """
        This is only checking if I can properly test views that
        call some task with .delay(), and the data goes to the test database.
        """
        # This has to be formatted exactly as an original spotify history
        file_history = [
            {
                "endTime": "2020-10-10 08:01",
                "msPlayed": 12345,
                "trackName": "Telegraph Road",
                "artistName": "Dire Straits",
            },
            {
                "endTime": "2020-10-11 08:11",
                "msPlayed": 54321,
                "trackName": "Be Yourself",
                "artistName": "Audioslave",
            },
        ]

        data = dict(file=(io.BytesIO(str.encode(json.dumps(file_history)))))

        # Send it to 'history' url
        response = self.client.post(reverse("history"), data, format="multipart")

        # Check if response ok
        self.assertEqual(response.status_code, 201)

        # Check if data in database
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=10, expected_amount=1
            )
        )
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=11, expected_amount=1
            )
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_insert_multiple_file(self):
        """
        This check if sending two separe history files to the upload history view is working
        """
        history_one = [
            {
                "endTime": "2020-10-10 08:01",
                "msPlayed": 12345,
                "trackName": "Telegraph Road",
                "artistName": "Dire Straits",
            },
            {
                "endTime": "2020-10-11 08:11",
                "msPlayed": 54321,
                "trackName": "Be Yourself",
                "artistName": "Audioslave",
            },
        ]

        # Same data but 1 year ahead
        history_two = [
            {
                "endTime": "2021-10-10 08:01",
                "msPlayed": 12345,
                "trackName": "Telegraph Road",
                "artistName": "Dire Straits",
            },
            {
                "endTime": "2021-10-11 08:11",
                "msPlayed": 54321,
                "trackName": "Be Yourself",
                "artistName": "Audioslave",
            },
        ]

        data = dict(
            file=(
                io.BytesIO(str.encode(json.dumps(history_one))),
                io.BytesIO(str.encode(json.dumps(history_two))),
            )
        )

        # Send it to 'history' url
        response = self.client.post(reverse("history"), data, format="multipart")

        # Check if response ok
        self.assertEqual(response.status_code, 201)

        # Check if data in database
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=10, expected_amount=1
            )
        )
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=11, expected_amount=1
            )
        )
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=10, day=10, expected_amount=1
            )
        )
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2021, month=10, day=11, expected_amount=1
            )
        )

    def test_insert_invalid_history_file(self):

        unvalid_data = "abcd"

        data = dict(file=(io.BytesIO(str.encode(unvalid_data)),))

        # Send it to 'history' url
        response = self.client.post(reverse("history"), data, format="multipart")

        # Check if error
        self.assertEqual(response.status_code, 400)

    def test_mock_spotipy_resp(self):
        """
        This is basically a test to check if I can mock the calls to spotify api
        by using patch on spotipy's search methods.
        """

        BASE_DIR = settings.BASE_DIR
        fake_resp_dir = os.path.join(BASE_DIR, "spotify", "tests", "fake_resp")

        # Here I'll load a fake spotify API response:
        # The track I've faked searching is "Sweet Sacrifice" by "Evanescence"
        with open(os.path.join(fake_resp_dir, "fake_search_resp.json"), "r") as f:
            fake_search_resp = json.load(f)

        # Track: Sweet Sacrifice
        with open(os.path.join(fake_resp_dir, "fake_track_resp.json"), "r") as f:
            fake_track_resp = json.load(f)

        # Album: The Open Door
        with open(os.path.join(fake_resp_dir, "fake_album_resp.json"), "r") as f:
            fake_album_resp = json.load(f)

        # Artist: Evanescence
        with open(os.path.join(fake_resp_dir, "fake_artist_resp.json"), "r") as f:
            fake_artist_resp = json.load(f)

        # Here I'll put some invalid track_name and artist_name.
        # If the Evanescence info I'm mocking was properly added to the database
        # means that the request was successfully mocked and no call was made to the API.
        history = [
            {
                "end_time": "2020-10-10 08:01",
                "ms_played": 12345,
                "track_name": "TRACK_THAT_DOES_NOT_EXIST",
                "artist_name": "ARTIST_THAT_DOES_NOT_EXIST",
            }
        ]

        @mock.patch("spotipy.Spotify.search", return_value=fake_search_resp)
        @mock.patch("spotipy.Spotify.track", return_value=fake_track_resp)
        @mock.patch("spotipy.Spotify.album", return_value=fake_album_resp)
        @mock.patch("spotipy.Spotify.artist", return_value=fake_artist_resp)
        def make_insert(*args, **kwargs):
            insert_track_batch_from_history(history)

        make_insert()

        # Check if track is in the database
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=10, expected_amount=1
            )
        )

        # Check if its the track from the fake resp data
        track = Tracks.objects.get(name="Sweet Sacrifice")

        # Assert all data is correct
        self.assertEqual(track.name, "Sweet Sacrifice")
        self.assertEqual(track.artists.first().name, "Evanescence")
        self.assertEqual(track.album.name, "The Open Door")

    def test_history_view_not_file(self):
        """
        Sending something other than a file to insert history view to check for error
        """
        resp = self.client.post(reverse("history"), {"key": "val"})

        self.assertEqual(resp.status_code, 400)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_history_varying_batch_sizes(self):
        """
        The history can accept very log history file sizes.
        And for that to work in a timely fashion it will split up the batches into different size
        and send it to celery.

        Here I'm just checking if that works ok without any error
        """

        single_entry = {
            "endTime": "2020-10-11 08:11",
            "msPlayed": 54321,
            "trackName": "Be Yourself",
            "artistName": "Audioslave",
        }

        # 15 entries -> default to batch size of 1
        small_batch = [single_entry for _ in range(15)]

        # 51 entries -> default to batch size of 10
        medium_batch = [single_entry for _ in range(51)]

        # 501 entries -> default to batch size of 100
        large_batch = [single_entry for _ in range(501)]

        # 1001 entries -> default to batch size of 200
        largest_batch = [single_entry for _ in range(1001)]

        for batch in [small_batch, medium_batch, large_batch, largest_batch]:
            data = dict(file=(io.BytesIO(str.encode(json.dumps(batch))),))

            # Patching the function that actually adds the tracks to database
            # to save time. Since adding 1000+ tracks takes a while.
            # And the purpose of the test is to see if batch size breaks something

            with mock.patch(
                "spotify.tasks.insert_track_from_history", return_value=True
            ):
                # Send it to 'history' url
                response = self.client.post(
                    reverse("history"), data, format="multipart"
                )

            # Check if response ok
            self.assertEqual(response.status_code, 201)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_history_with_some_invalid_entries(self):
        """
        When iterating over the history entries (track name / artist name)
        if some of them are invalid for whatever reason, instead of stopping everything
        the endpoint will continue iterating and try them all.

        So here I'll just put some invalid data in the middle of valid ones and check
        if the valid ones are still added to the database
        """

        fake_history = [
            {
                "endTime": "2020-10-10 08:01",
                "msPlayed": 12345,
                "trackName": "Telegraph Road",
                "artistName": "Dire Straits",
            },
            {
                "this": "one",
                "is": "wrong",
            },
            {
                "endTime": "this one",
                "msPlayed": True,
                "trackName": "Is also",
                "artistName": "wrong",
            },
            {
                "endTime": "2020-10-11 08:11",
                "msPlayed": 54321,
                "trackName": "Be Yourself",
                "artistName": "Audioslave",
            },
        ]
        data = dict(file=(io.BytesIO(str.encode(json.dumps(fake_history))),))

        # Send it to 'history' url
        response = self.client.post(reverse("history"), data, format="multipart")

        # Check if response ok
        self.assertEqual(response.status_code, 201)

        # Check if the two valid ones were added
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=10, expected_amount=1
            )
        )

        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2020, month=10, day=11, expected_amount=1
            )
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_recently_played_view(self):
        """
        This one will call a empty post to "refresh_recently_played", which makes
        the view call its method to get all recently played tracks.

        Here I'll be mocking the recently played response from the api.

        On my mock response I have three tracks, played at 2018-01-01, 2018-01-02, 2018-01-03,
        from the three tracks I have in the fixture: Telegraph Road, Be Yourself, I am The Highway, respectively.
        """

        BASE_DIR = settings.BASE_DIR
        fake_resp_dir = os.path.join(BASE_DIR, "spotify", "tests", "fake_resp")

        with open(
            os.path.join(fake_resp_dir, "fake_recently_played_resp.json"), "r"
        ) as f:
            fake_recently_played_data = json.load(f)

        @mock.patch(
            "spotipy.Spotify.current_user_recently_played",
            return_value=fake_recently_played_data,
        )
        def make_request(*args, **kwargs):
            resp = self.client.post(reverse("refresh_recently_played"), {})
            return resp

        resp = make_request()

        # Check if response ok
        self.assertEqual(resp.status_code, 201)

        # Check if data was inserted
        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2018, month=1, day=1, expected_amount=1
            )
        )

        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2018, month=1, day=2, expected_amount=1
            )
        )

        self.assertTrue(
            self.amount_of_entries_that_day(
                year=2018, month=1, day=3, expected_amount=1
            )
        )

        # Check if it's the right track
        track = UserActivity.objects.get(
            played_at__year=2018, played_at__month=1, played_at__day=1
        )
        self.assertEqual(track.track.name, "Telegraph Road")

        track = UserActivity.objects.get(
            played_at__year=2018, played_at__month=1, played_at__day=2
        )
        self.assertEqual(track.track.name, "Be Yourself")

        track = UserActivity.objects.get(
            played_at__year=2018, played_at__month=1, played_at__day=3
        )

        self.assertEqual(track.track.name, "I Am the Highway")
