from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.user_activity_serializers import (
    AvailableYearsSerializer,
    SimpleUserActivitySerializer,
    TimePlayedSerializer,
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
from django.db.models import Sum
from django.db.models.functions import Trunc
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
import logging

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
        # Qty defaults to 10
        qty = self.request.query_params.get("qty", 10)
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
        qty = validate_qty_query_params(qty)
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
