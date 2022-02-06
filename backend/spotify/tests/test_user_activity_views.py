from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from spotify.tasks import insert_track_batch_from_history
from datetime import datetime, timedelta, timezone
from spotify.models import UserActivity
from django.test.utils import tag


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

        user = User.objects.create_superuser("admin", "admin@admin.com", "admin")
        self.client.force_authenticate(user)

        # This is a way of skipping the insert setup.
        # Its placed after the auth because the user has to be authenticated.
        method = getattr(self, self._testMethodName)
        tags = getattr(method, "tags", {})
        if "skip_setup" in tags:
            return

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

    @tag("skip_setup")
    def test_recent_user_activity_periodicity(self):
        # To test the weekly periodicity I have to make sure to put entrie
        # in the middle of weeks.
        this_weeks_wednesday = (
            datetime.today()
            # This gets monday
            - timedelta(days=datetime.today().weekday())
            # + 2 days for wednesday
            + timedelta(days=2)
        )

        # Add one track track per week each wednesday for the past 5 weeks
        entries = [
            {
                "end_time": (this_weeks_wednesday - timedelta(days=i * 7)).strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 15 * 60_000,
            }
            for i in range(5)
        ]

        # print(entries)

        # Insert it into the database
        insert_track_batch_from_history(entries)

        # Query for weekly data
        res = self.client.get(
            reverse("time_played"), {"periodicity": "weekly", "days": 500}
        )

        # Check if ok
        self.assertEqual(res.status_code, 200)

        # Check if the data is correct
        self.assertEqual(res.data["total_minutes_played"], 15 * 5)

        # Check if returned the correct number of weeks
        self.assertEqual(len(res.data["items"]), 5)

        # The weeks truncate on the monday. So just check if the last is
        # this weeks monday
        this_monday = datetime.today() - timedelta(days=datetime.today().weekday())
        self.assertEqual(
            res.data["items"][-1]["date"], this_monday.strftime("%Y-%m-%d")
        )

        # Check if the second to last is the previous monday
        previous_monday = this_monday - timedelta(days=7)
        self.assertEqual(
            res.data["items"][-2]["date"], previous_monday.strftime("%Y-%m-%d")
        )

    @tag("skip_setup")
    def test_first_and_last_day_year(self):
        """
        Test for a given year if the endpoint to get the first and most recent date
        of a time activity works.
        """

        # First make the request without adding any data. Should throw error
        res = self.client.get(reverse("first_and_last_day_year"), {"year": 2021})

        # Check if error
        self.assertEqual(res.status_code, 404)

        # Insert one entry in the 2021-02-01 and another in 2021-11-01
        entries = [
            {
                "end_time": "2021-02-01 12:00",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 15 * 60_000,
            },
            {
                "end_time": "2021-11-01 12:00",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 15 * 60_000,
            },
        ]

        # Insert it into the database
        insert_track_batch_from_history(entries)

        # Now make the request
        res = self.client.get(reverse("first_and_last_day_year"), {"year": 2021})

        # Check if ok
        self.assertEqual(res.status_code, 200)

        # Check if the data is correct
        self.assertEqual(res.data["first_day"], "2021-02-01")
        self.assertEqual(res.data["last_day"], "2021-11-01")

    @tag("skip_setup")
    def test_user_activity_statistics(self):
        """
        Test for the view of general user statistics
        """

        # I'll add 10 / 20 minutes in two days of the 2021
        entries = [
            {
                "end_time": "2021-05-01 12:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 10 * 60_000,
            },
            {
                "end_time": "2021-06-01 14:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 20 * 60_000,
            },
        ]

        # Insert it into the database
        insert_track_batch_from_history(entries)

        # Now make the request
        res = self.client.get(reverse("user_activity_statistics"), {"year": 2021})

        # Check if ok
        self.assertEqual(res.status_code, 200)

        # Check if the average per day is 30/365
        self.assertEqual(res.data["average_minutes_per_day"], round(30 / 365, 2))

        # Check if total time played in days is 30/60/24
        self.assertEqual(res.data["total_time_played_in_days"], round(30 / 60 / 24, 2))

        # 2021-06-01 is a Tuesday, so the most played day of week in 2021 should be Tuesday
        self.assertEqual(res.data["day_of_week_most_activity"], "Tuesday")

        # The most played hour of day should be 2 pm
        self.assertEqual(res.data["hour_of_day_most_activity"], "02 pm")

    @tag("skip_setup")
    def test_time_played_per_hour_of_day(self):
        """
        Tests if the endpoint to get the time played per hour of day works
        """

        entries = [
            {
                "end_time": "2021-05-01 12:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 10 * 60_000,
            },
            {
                "end_time": "2021-06-01 14:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 20 * 60_000,
            },
            {
                "end_time": "2021-07-01 21:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 30 * 60_000,
            },
        ]

        # Insert it into the database
        insert_track_batch_from_history(entries)

        # Now make the request
        res = self.client.get(reverse("time_played_per_hour_of_day"), {"year": 2021})

        # Check if ok
        self.assertEqual(res.status_code, 200)

        # Check if the data is correct
        # The first data point should be 12 am (midnight) and be 0
        self.assertEqual(res.data[0]["hour"], "12 am")
        self.assertEqual(res.data[0]["minutes_played"], 0)

        # The last has to be 11pm (23h) and also be 0
        self.assertEqual(res.data[-1]["hour"], "11 pm")
        self.assertEqual(res.data[-1]["minutes_played"], 0)

        # Now get the point for 12 pm (midday) and check if its 10 min
        self.assertEqual(res.data[12]["hour"], "12 pm")
        self.assertEqual(res.data[12]["minutes_played"], 10)

        # Check for rest of data inserted
        self.assertEqual(res.data[14]["hour"], "02 pm")
        self.assertEqual(res.data[14]["minutes_played"], 20)

        # Check for rest of data inserted
        self.assertEqual(res.data[21]["hour"], "09 pm")
        self.assertEqual(res.data[21]["minutes_played"], 30)

    @tag("skip_setup")
    def test_time_played_per_day_of_week(self):
        """
        Tests if the endpoint to get the time played per weekday works
        """

        entries = [
            # Saturday
            {
                "end_time": "2021-05-01 12:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 10 * 60_000,
            },
            # Tuesday
            {
                "end_time": "2021-06-01 14:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 20 * 60_000,
            },
            # Thursday
            {
                "end_time": "2021-07-01 15:30",
                "artist_name": "Audioslave",
                "track_name": "Be Yourself",
                "ms_played": 30 * 60_000,
            },
        ]

        # Insert it into the database
        insert_track_batch_from_history(entries)

        # Now make the request
        res = self.client.get(reverse("time_played_per_day_of_week"), {"year": 2021})

        # Check if ok
        self.assertEqual(res.status_code, 200)

        # Check if the data is correct
        # The first data point should be Sunday and 0
        self.assertEqual(res.data[0]["day_of_week"], "Sunday")
        self.assertEqual(res.data[0]["minutes_played"], 0)

        # The last has to be Saturday and 10 minutes
        self.assertEqual(res.data[-1]["day_of_week"], "Saturday")
        self.assertEqual(res.data[-1]["minutes_played"], 10)

        # Index 2 is tuesday, so it should be 20 minutes
        self.assertEqual(res.data[2]["day_of_week"], "Tuesday")
        self.assertEqual(res.data[2]["minutes_played"], 20)

        # Index 4 is Thursday, so it should be 30 minutes
        self.assertEqual(res.data[4]["day_of_week"], "Thursday")
        self.assertEqual(res.data[4]["minutes_played"], 30)
