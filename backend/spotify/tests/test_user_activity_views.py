from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from spotify.tasks import insert_track_batch_from_history
from datetime import datetime, timedelta, timezone
from spotify.models import UserActivity


class TestUserActivityViews(APITestCase):
    """ """

    fixtures = ["albums.json", "artists.json", "genres.json", "tracks.json"]

    def setUp(self):
        """
        The plan here is to add 1 track per day for the past
        15 days (today + 14 days before).

        The most recent listened to for 15min, and then 14, and so on,
        and so forth. Just for them to have different times in a predictable manner.

        The different tracks do not matter here, so it will always be the same one,
        from the fixtures.

        # TODO: Some tests here fail at specific hours of day. The ones that take into account TZ.
        # I'll have to figure it out later.
        """

        user = User.objects.create_superuser('admin', 'admin@admin.com', "admin")
        self.client.force_authenticate(user)

        today = datetime.today()
        # Set time as 1 am
        today = today.replace(hour=1, minute=0, second=0, microsecond=0)

        self.history_data = [
            {
                "end_time": (today - timedelta(days=i)).strftime("%Y-%m-%d %H:%M"),
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": (15 - i) * 60_000,
            }
            for i in range(15)
        ]

        # Insert it into the database
        insert_track_batch_from_history(self.history_data)

    def test_setup_insert(self):
        """
        Test that the setup worked
        """
        self.assertEqual(UserActivity.objects.count(), 15)

    def test_available_years(self):
        """
        Check if returns the correct years in user activity
        """
        res = self.client.get(reverse("available_years"))
        self.assertEqual(res.status_code, 200)

        year_list = [item["year"] for item in res.data]

        current_year = datetime.today().year

        # This might be a different year depending on the day.
        # Since the setup adds activity the last 15 days
        year_15_days_ago = (datetime.today() - timedelta(days=15)).year

        if current_year == year_15_days_ago:
            self.assertEqual(year_list, [current_year])
        else:
            self.assertEqual(year_list, [current_year, year_15_days_ago])

    def test_simple_time_played(self):
        """
        Test the endpoint without any params just to see if everything
        matches what's expected from the setup
        """

        res = self.client.get(reverse("time_played"))

        self.assertEqual(res.status_code, 200)

        # By default it returns the last 7 days (today + 6).
        # So lets check if the sum of minutes
        # is 15+14+13+12+11+10+9 = 84
        self.assertEqual(
            res.data["total_minutes_played"], 15 + 14 + 13 + 12 + 11 + 10 + 9
        )

        # Last week should've been 8+7+6+5+4+3+2 = 35
        # So the growth is (84 - 35) / 35
        self.assertEqual(res.data["growth"], (84 - 35) / 35)

    def test_time_played_timezone(self):
        """
        The Time Played can take into account time zone.

        All spotify's data comes as UTC. And the server stores everything as UTC.

        When we are looking at day boundaries though, and I want to know how many hours
        i've listened to 'yesterday', than it would be better to take my time zone into account.

        As of right now, all tracks added on setUp are at 1am. Which means that if the user
        is actually from a timezone thats 1 hour behind, then it should change the result from the query.
        """

        # Going through this slowly because dealing with timezones is hell.

        # Lets set the timezone to Sao Paulo, which is UTC-3.
        tz_name = "America/Sao_Paulo"

        # So, there was a track added in setUp played 'today' (server time) at 1 am.
        # But if it was truly spotify data and my timezone is UTC-3, it means that
        # I've actually listened to that song 'yesterday' in server time.

        # So now, if here I get today at server time, time latest date the endpoint
        # should return when I query for recently_played with a timezone is actually 'yesterday'.
        today_server_time = datetime.today()
        yesterday_server_time = today_server_time - timedelta(days=1)
        yesterday_str = yesterday_server_time.strftime("%Y-%m-%d")

        # Lets query the endpoint now
        res = self.client.get(reverse("time_played"), {"timezone": tz_name, "days": 7})
        self.assertEqual(res.status_code, 200)

        # Check if the latest day is actually 'yesterday' at server time
        latest_day = res.data["items"][-1]["date"]

        self.assertEqual(latest_day, yesterday_str)

        # And just as before, the time played should be
        # 15+14+13+12+11+10+9 = 84 minutes
        self.assertEqual(
            res.data["total_minutes_played"], 15 + 14 + 13 + 12 + 11 + 10 + 9
        )

    def test_recent_user_activity_view(self):
        """
        Test the endpoint to get the user activity.
        """

        # Make the request, getting the 5 most recent
        res = self.client.get(reverse("recently_played"), {"qty": 5})

        # Check if ok
        self.assertEqual(res.status_code, 200)

        # Check if the data is correct, which means that the most recent
        # gotta be for 15 minutes played
        self.assertEqual(res.data[0]["ms_played"], 15 * 60_000)

        # The last one hast to be (5th) has to be 11 minutes played
        self.assertEqual(res.data[-1]["ms_played"], 11 * 60_000)
