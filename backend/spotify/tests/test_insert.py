from rest_framework.test import APITestCase
from django.test.utils import tag
from django.db.models import Sum
from spotify.models import Albums, Artists, Tracks, Genres, UserActivity
from spotify.tasks import insert_track_batch_from_history, insert_track_entry
from spotify.helpers import insert_user_activity
from datetime import datetime, timedelta


class TestInsert(APITestCase):
    """
    Here i'm going to be testing the logic to insert USER ACTIVITY into the database.
    For that I mean that i'll be checking the UserActivity model and also the History related model.

    Inserting artists/tracks/albums/genres into the DB requires API calls to Spotify. So i'll refrain from doing that,
    since it's too much of a hassle to mock the API calls.

    When trying to insert UserActivity/History this app checks if the tracks, albums, artists, genres already exist in the DB,
    and if so, it will not request them from Spotify API.

    As of right now in the fixture I added two artists, three tracks, three albums and a few genres.

    Artists: Audioslave, Dire Straits.
    Tracks: Audioslave - Be Yourself, Audioslave - I Am the Highway, Dire Straits - Telegraph Road.
    Albums: Audioslave - Audioslave, Audioslave - Out of Exile, Dire Straits - Love Over Gold.
    Genres (some): rock, classic rock, nu metal, alternative rock.
    """

    fixtures = ["albums.json", "artists.json", "genres.json", "tracks.json"]

    def setUp(self):
        """
        Creates a mock history from spotify. Adds it to the database.
        """
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

    def test_user_activity(self):
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
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=1, played_at__day=1
            ).count(),
            1,
        )
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=2, played_at__day=1
            ).count(),
            1,
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

    def test_history_existing_data(self):
        """
        This will test if my checks for existing data are correct.

        Here I'll be trying to add the exact same history data twice, once in the setup, another in this method.

        It's exactly the same tests as the method above.
        """
        # Insert it into the database
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
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=1, played_at__day=1
            ).count(),
            1,
        )
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=2, played_at__day=1
            ).count(),
            1,
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

    def unpack_track_data(self, track):
        """
        Inserting a track as a entry requires some specific fields as will be shown below.
        Since this is a common task for some of the following tests, I'll create this function here.
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

    def test_track_entry_insert(self):
        """
        There are two flows for entering data into the database. One is longer and has to SEARCH the spotify api (history),
        and the other already has ID of tracks and more info, then it's just a matter of querying for artist and album id.

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
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=1, played_at__day=1
            ).count(),
            2,
        )

        # Check if the ms_played is also correct,
        total_ms_day = track_data["ms_played"] + self.history_data[0]["ms_played"]
        self.assertEqual(
            UserActivity.objects.filter(
                played_at__year=2021, played_at__month=1, played_at__day=1
            ).aggregate(Sum("ms_played"))["ms_played__sum"],
            total_ms_day,
        )

    def test_insert_equivalent_activity(self):
        """
        There is some logic on the function insert_user_activity that shouldn't
        let two similar activities be added. Which means that if I try to insert
        another entry that was played at the same minute (but not equal) than one
        existing, it shouldn't add it!
        """

        def one_activity_that_day(year, month, day):
            """Helper function to check if at that day there was only one entry in user activity"""
            return (
                UserActivity.objects.filter(
                    played_at__year=year, played_at__month=month, played_at__day=day
                ).count()
                == 1
            )

        track = Tracks.objects.get(name="I Am the Highway")

        # I'll try to add comparing to the I Am the Highway played at
        # 2021-04-01, with end time of 13:00:00 and was played for 40000 ms.
        # To get the played_at from the end_time I have to subtract the duration.
        # The played_at for this track is: 2021-04-01T12:59:20.000Z

        # The exact same time but formated very accurately
        played_at = "2021-04-01T12:59:20.000Z"
        ms_played = 1337
        from_import = False

        # I'll add this one directly with the function used by insert_track_entry
        insert_user_activity(track, ms_played, played_at, from_import)

        # Now check if was correctly skipped
        self.assertTrue(one_activity_that_day(2021, 4, 1))

        # Now, let's try with a different time. Just 10 seconds before
        # TODO: Pqq isso ta dando errado??? Nao ta pegando o equivalent activites??
        played_at = "2021-04-01T12:59:10.000Z"
        insert_user_activity(track, ms_played, played_at, from_import)
        self.assertTrue(one_activity_that_day(2021, 4, 1))

        # Trying with one minute difference, this is literally the max it should be
        # to still be marked as "same" entry and not be added
        # played_at = "2021-04-01T12:58:50.000Z"
        # insert_user_activity(track, ms_played, played_at, from_import)
        # self.assertTrue(one_activity_that_day(2021, 4, 1))
