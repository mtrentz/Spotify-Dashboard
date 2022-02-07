from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.track_serializers import (
    TopTracksSerializer,
    UniqueTracksSerializer,
)
from django.db.models import Sum, Count
from ..models import Tracks
from datetime import datetime, timedelta, timezone
from ..helpers import (
    validate_days_query_param,
    validate_qty_query_params,
    validate_and_parse_date_selection_query_parameters,
    validate_timezone_query_params,
    filter_model_by_date_selection,
    filter_model_by_date_selection_previous_period,
    calculate_growth,
)
import pytz


class TopPlayedTracksView(ListAPIView):
    """
    This will return the top tracks played by time.

    It can be filtered by:
        - days: the number of days to look back
        - year: the year to look back
        - date_start: the start date to look back
        - date_end: the end date to look back
        - qty: the number of artists to return

    Some of them are exclusive, meaning that only one of them can be passed.
    You can either filter by days, year or date_range. If none were passed
    the endpoint will default to showing the top 10 artists for the last 7 days.
    """

    serializer_class = TopTracksSerializer

    def get_queryset(self):
        days_param = self.request.query_params.get("days", None)
        year_param = self.request.query_params.get("year", None)
        date_start_param = self.request.query_params.get("date_start", None)
        date_end_param = self.request.query_params.get("date_end", None)
        # Qty defaults to 10
        qty = self.request.query_params.get("qty", 10)
        # Defaults to UTC
        tz_name = self.request.query_params.get("timezone", "UTC")

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
        qty = validate_qty_query_params(qty)
        tz_name = validate_timezone_query_params(tz_name)

        tzinfo = pytz.timezone(tz_name)

        objects = filter_model_by_date_selection(
            Tracks,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="useractivity__played_at",
        )

        items = objects.annotate(
            time_played_ms=Sum("useractivity__ms_played")
        ).order_by("-time_played_ms")[:qty]

        queryset = []

        for item in items:
            queryset.append(
                {
                    "track": item.name,
                    "album": item.album.name,
                    "album_cover": item.album.art_sm,
                    "artists": [a.name for a in item.artists.all()],
                    "minutes_played": item.time_played_ms / 60_000,
                }
            )

        return queryset


class UniqueTracksView(RetrieveAPIView):
    serializer_class = UniqueTracksSerializer

    def get_queryset(self):
        days_param = self.request.query_params.get("days", None)
        year_param = self.request.query_params.get("year", None)
        date_start_param = self.request.query_params.get("date_start", None)
        date_end_param = self.request.query_params.get("date_end", None)
        # Defaults to UTC
        tz_name = self.request.query_params.get("timezone", "UTC")

        # Validate the parameters
        (
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
        ) = validate_and_parse_date_selection_query_parameters(
            days_param,
            year_param,
            date_start_param,
            date_end_param,
        )
        tz_name = validate_timezone_query_params(tz_name)

        tzinfo = pytz.timezone(tz_name)

        objects = filter_model_by_date_selection(
            Tracks,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="useractivity__played_at",
        )

        # Calculate amount of unique tracks on the period selected
        count = (
            objects
            # Group tracks by ms_played
            .annotate(time_played_ms=Sum("useractivity__ms_played"))
            # Filter by those listened to more than 2 minutes (120000 ms)
            .filter(time_played_ms__gte=120000)
            # Count by unique tracks
            .aggregate(Count("sp_id", distinct=True))
        )

        previous_objects = filter_model_by_date_selection_previous_period(
            Tracks,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="useractivity__played_at",
        )

        previous_count = (
            previous_objects.annotate(time_played_ms=Sum("useractivity__ms_played"))
            .filter(time_played_ms__gte=120000)
            .aggregate(Count("sp_id", distinct=True))
        )

        # Calculate the growth
        growth = calculate_growth(previous_count["sp_id__count"], count["sp_id__count"])

        return {"count": count["sp_id__count"], "growth": growth}

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset
