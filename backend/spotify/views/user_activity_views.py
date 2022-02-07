from rest_framework.exceptions import ParseError, NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.user_activity_serializers import (
    AvailableYearsSerializer,
    FirstAndLastDayYearSerializer,
    SimpleUserActivitySerializer,
    TimePlayedPerDayOfWeekSerializer,
    TimePlayedPerHourOfDaySerializer,
    TimePlayedSerializer,
    UserActivityStatisticsSerializer,
)
from ..models import UserActivity
from ..helpers import (
    validate_and_parse_date_selection_query_parameters,
    validate_qty_query_params,
    validate_timezone_query_params,
    filter_model_by_date_selection,
    filter_model_by_date_selection_previous_period,
    validate_periodicity_params,
    calculate_growth,
)
from django.db.models import Sum, Min, Max, Avg
from django.db.models.functions import Trunc, ExtractWeekDay, ExtractHour
import pytz
import logging
from datetime import datetime

logger = logging.getLogger("django")


class RecentUserActivityView(ListAPIView):
    serializer_class = SimpleUserActivitySerializer

    def get_queryset(self):
        # How many tracks to return, defaults to 10, func will raise for errors
        qty = validate_qty_query_params(self.request.query_params.get("qty", 10))

        items = UserActivity.objects.order_by("-played_at")[:qty]

        queryset = []

        for item in items:
            queryset.append(
                {
                    "track": item.track.name,
                    "album": item.track.album.name,
                    "album_cover": item.track.album.art_sm,
                    "artists": [a.name for a in item.track.artists.all()],
                    "played_at": item.played_at,
                    "ms_played": item.ms_played,
                }
            )

        return queryset


class TimePlayedView(RetrieveAPIView):
    serializer_class = TimePlayedSerializer

    def get_queryset(self):
        days_param = self.request.query_params.get("days", None)
        year_param = self.request.query_params.get("year", None)
        date_start_param = self.request.query_params.get("date_start", None)
        date_end_param = self.request.query_params.get("date_end", None)
        # Defaults to daily
        periodicity = self.request.query_params.get("periodicity", "daily")
        # Defaults to UTC
        tz_name = self.request.query_params.get("timezone", "UTC")
        tzinfo = pytz.timezone(tz_name)

        # Validate the parameters
        (
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
        ) = validate_and_parse_date_selection_query_parameters(
            days_param, year_param, date_start_param, date_end_param
        )
        periodicity = validate_periodicity_params(periodicity)
        tz_name = validate_timezone_query_params(tz_name)

        tzinfo = pytz.timezone(tz_name)

        objects = filter_model_by_date_selection(
            UserActivity,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="played_at",
        )

        # Here I have the amount played day by day in the current period.
        time_played_by_period = (
            objects
            # Truncate period
            .annotate(period=Trunc("played_at", periodicity, tzinfo=tzinfo))
            # Get the values for period
            .values("period")
            # Sum the ms_played for each day
            .annotate(time_played_ms=Sum("ms_played"))
            # Order so the oldest is first
            .order_by("period")
        )

        # Sum the ms_played for the current period
        ms_played_current = time_played_by_period.aggregate(Sum("time_played_ms"))[
            "time_played_ms__sum"
        ]

        if not ms_played_current:
            ms_played_current = 0

        previous_objects = filter_model_by_date_selection_previous_period(
            UserActivity,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="played_at",
        )

        ms_played_previous = (
            previous_objects
            # Aggregate the sum
            .aggregate(Sum("ms_played"))
        )["ms_played__sum"]

        if not ms_played_previous:
            ms_played_previous = 0

        # Items is going to be a list of objects {'date': date, 'minutes_played': int}
        items = []

        for obj in time_played_by_period:
            items.append(
                {
                    "date": obj["period"].strftime("%Y-%m-%d"),
                    "minutes_played": obj["time_played_ms"] / 60_000,
                }
            )

        growth = calculate_growth(ms_played_previous, ms_played_current)

        queryset = {
            "items": items,
            "total_minutes_played": ms_played_current / 60_000,
            "growth": round(growth, 2),
            "tz_name": tz_name,
        }

        return queryset

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset


class AvailableYearsView(ListAPIView):
    "Returns the years available for the user activity"
    serializer_class = AvailableYearsSerializer

    def get_queryset(self):

        # Defaults to UTC if not any (or invalid) is provided
        tz_name = validate_timezone_query_params(
            self.request.query_params.get("timezone", "UTC")
        )
        tzinfo = pytz.timezone(tz_name)

        items = (
            UserActivity.objects.annotate(
                year=Trunc("played_at", "year", tzinfo=tzinfo)
            )
            .values("year")
            .distinct("year")
        )

        if items:
            queryset = [{"year": i["year"].year} for i in items]
        else:
            queryset = []

        return queryset


class FirstAndLastDayYearView(RetrieveAPIView):
    """
    For a given year and timezone, returns the first and last day of user activity.
    """

    serializer_class = FirstAndLastDayYearSerializer

    def get_queryset(self):
        year_param = self.request.query_params.get("year", None)
        tz_name = self.request.query_params.get("timezone", "UTC")

        # Validate the parameters
        (
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
        ) = validate_and_parse_date_selection_query_parameters(
            None, year_param, None, None
        )
        tz_name = validate_timezone_query_params(tz_name)

        if not year_param:
            raise ParseError("The year parameter is required")

        tzinfo = pytz.timezone(tz_name)

        objects = filter_model_by_date_selection(
            UserActivity,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="played_at",
        )

        # Get the object with lowest and highest date
        first_and_last_day = objects.aggregate(
            first_day=Min("played_at"), last_day=Max("played_at")
        )

        if not first_and_last_day["first_day"] or not first_and_last_day["last_day"]:
            raise NotFound("No data found for the given year")

        queryset = {
            "first_day": first_and_last_day["first_day"].strftime("%Y-%m-%d"),
            "last_day": first_and_last_day["last_day"].strftime("%Y-%m-%d"),
        }

        return queryset

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset


class UserActivityStatisticsView(RetrieveAPIView):
    """
    For a given year and timezone return some diverse statistics, for example:
        - day with highest time played
        - what time of day the user mostly listens to spotify
    etc...
    """

    serializer_class = UserActivityStatisticsSerializer

    def get_queryset(self):
        year_param = self.request.query_params.get("year", None)
        tz_name = self.request.query_params.get("timezone", "UTC")

        # Validate the parameters
        (
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
        ) = validate_and_parse_date_selection_query_parameters(
            None, year_param, None, None
        )
        tz_name = validate_timezone_query_params(tz_name)

        if not year_param:
            raise ParseError("The year parameter is required")

        tzinfo = pytz.timezone(tz_name)

        objects = filter_model_by_date_selection(
            UserActivity,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="played_at",
        )

        if objects.count() == 0:
            raise NotFound("No data found for the given year")

        # Getting average minutes per day, and total 'days' played in total
        total_ms_played = objects.aggregate(total=Sum("ms_played"))["total"]

        average_minutes_per_day = total_ms_played / (365 * 60_000)

        total_time_played_in_days = total_ms_played / 60_000 / 60 / 24

        # Getting the day of the week which user most listened to spotify
        day_of_week_most_activity = (
            (
                objects.annotate(weekday=ExtractWeekDay("played_at", tzinfo=tzinfo))
                .values("weekday")
                .annotate(Sum("ms_played"))
            )
            .order_by("-ms_played__sum")
            .first()
        )["weekday"]

        # Map weekday to name
        weekday_map = {
            "1": "Sunday",
            "2": "Monday",
            "3": "Tuesday",
            "4": "Wednesday",
            "5": "Thursday",
            "6": "Friday",
            "7": "Saturday",
        }

        # Getting the hour of day which user most listened to spotify
        hour_of_day_most_activity = (
            objects.annotate(hour=ExtractHour("played_at", tzinfo=tzinfo))
            .values("hour")
            .annotate(Sum("ms_played"))
            .order_by("-ms_played__sum")
        ).first()["hour"]

        # Pass to am/pm
        hour_of_day_most_activity = (
            datetime.strptime(str(hour_of_day_most_activity), "%H")
            .strftime("%I %p")
            .lower()
        )

        queryset = {
            "average_minutes_per_day": round(average_minutes_per_day, 2),
            "total_time_played_in_days": round(total_time_played_in_days, 2),
            "day_of_week_most_activity": weekday_map[str(day_of_week_most_activity)],
            "hour_of_day_most_activity": hour_of_day_most_activity,
        }

        return queryset

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset


class TimePlayedPerHourOfDayView(ListAPIView):
    """
    Returns the amount played in minutes of day for each
    of the 24 hours.
    """

    serializer_class = TimePlayedPerHourOfDaySerializer

    def get_queryset(self):
        days_param = self.request.query_params.get("days", None)
        year_param = self.request.query_params.get("year", None)
        date_start_param = self.request.query_params.get("date_start", None)
        date_end_param = self.request.query_params.get("date_end", None)
        # Defaults to daily
        periodicity = self.request.query_params.get("periodicity", "daily")
        # Defaults to UTC
        tz_name = self.request.query_params.get("timezone", "UTC")
        tzinfo = pytz.timezone(tz_name)

        # Validate the parameters
        (
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
        ) = validate_and_parse_date_selection_query_parameters(
            days_param, year_param, date_start_param, date_end_param
        )
        periodicity = validate_periodicity_params(periodicity)
        tz_name = validate_timezone_query_params(tz_name)

        tzinfo = pytz.timezone(tz_name)

        objects = filter_model_by_date_selection(
            UserActivity,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="played_at",
        )

        if objects.count() == 0:
            raise NotFound("No data found for the given year")

        # Getting the hour of day which user most listened to spotify
        hour_of_day_most_activity = (
            objects.annotate(hour=ExtractHour("played_at", tzinfo=tzinfo))
            .values("hour")
            .annotate(Sum("ms_played"))
        )

        # Unpack the values into a dictionary of {hour_str: ms_played, ...}
        ms_per_hour = {
            str(v["hour"]): v["ms_played__sum"] for v in hour_of_day_most_activity
        }

        # I have to make sure that if there was no activity
        # for a certain hour, its value will be 0.
        hours_of_day = [str(i) for i in range(24)]

        # Simple func to convert a 24h time to 12h: 14h -> 02 pm
        convert_am_pm = (
            lambda x: datetime.strptime(str(x), "%H").strftime("%I %p").lower()
        )

        queryset = []

        for h in hours_of_day:
            if h in ms_per_hour:
                queryset.append(
                    {
                        "hour": convert_am_pm(h),
                        "minutes_played": round(ms_per_hour[h] / 60_000, 2),
                    }
                )
            else:
                queryset.append({"hour": convert_am_pm(h), "minutes_played": 0})

        return queryset


class TimePlayedPerDayOfWeekView(ListAPIView):
    """
    Returns the amount played in minutes on each day of the week
    """

    serializer_class = TimePlayedPerDayOfWeekSerializer

    def get_queryset(self):
        days_param = self.request.query_params.get("days", None)
        year_param = self.request.query_params.get("year", None)
        date_start_param = self.request.query_params.get("date_start", None)
        date_end_param = self.request.query_params.get("date_end", None)
        # Defaults to daily
        periodicity = self.request.query_params.get("periodicity", "daily")
        # Defaults to UTC
        tz_name = self.request.query_params.get("timezone", "UTC")
        tzinfo = pytz.timezone(tz_name)

        # Validate the parameters
        (
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
        ) = validate_and_parse_date_selection_query_parameters(
            days_param, year_param, date_start_param, date_end_param
        )
        periodicity = validate_periodicity_params(periodicity)
        tz_name = validate_timezone_query_params(tz_name)

        tzinfo = pytz.timezone(tz_name)

        objects = filter_model_by_date_selection(
            UserActivity,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="played_at",
        )

        if objects.count() == 0:
            raise NotFound("No data found for the given year")

        # Getting the hour of day which user most listened to spotify
        day_of_week_most_activity = (
            objects.annotate(weekday=ExtractWeekDay("played_at", tzinfo=tzinfo))
            .values("weekday")
            .annotate(Sum("ms_played"))
        )

        # Unpack the values into a dictionary of {weekday_num: ms_played, ...}, where 1 = Sunday
        ms_per_weekday = {
            str(v["weekday"]): v["ms_played__sum"] for v in day_of_week_most_activity
        }

        # I have to make sure that if there was no activity
        # for a certain day, it will show up as 0
        weekdays_num = [str(i) for i in range(1, 8)]

        weekday_map = {
            "1": "Sunday",
            "2": "Monday",
            "3": "Tuesday",
            "4": "Wednesday",
            "5": "Thursday",
            "6": "Friday",
            "7": "Saturday",
        }

        queryset = []

        for w in weekdays_num:
            if w in ms_per_weekday:
                queryset.append(
                    {
                        "day_of_week": weekday_map[w],
                        "minutes_played": round(ms_per_weekday[w] / 60_000, 2),
                    }
                )
            else:
                queryset.append({"day_of_week": weekday_map[w], "minutes_played": 0})

        return queryset
