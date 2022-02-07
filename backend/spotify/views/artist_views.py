from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from django.db.models.functions import Trunc
from ..serializers.artist_serializers import (
    TopArtistsSerializers,
    UniqueArtistsSerializer,
)
from ..models import Artists
from django.db.models import Sum, Count
from datetime import datetime, timedelta, timezone
import pytz
from ..helpers import (
    validate_and_parse_date_selection_query_parameters,
    validate_qty_query_params,
    validate_timezone_query_params,
    filter_model_by_date_selection,
    filter_model_by_date_selection_previous_period,
    calculate_growth,
)


class TopPlayedArtistsView(ListAPIView):
    """
    This will return the top artists played by time.

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

    serializer_class = TopArtistsSerializers

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
            Artists,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="tracks__useractivity__played_at",
        )

        # Now that I have the objects filtered by date, I can aggregate
        # and get the correct ammount to return.
        items = objects.annotate(
            time_played_ms=Sum("tracks__useractivity__ms_played")
        ).order_by("-time_played_ms")[:qty]

        queryset = []

        for item in items:
            queryset.append(
                {
                    "artist": item.name,
                    "minutes_played": item.time_played_ms / 60_000,
                }
            )

        return queryset


class UniqueArtistsView(RetrieveAPIView):
    serializer_class = UniqueArtistsSerializer

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
            Artists,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="tracks__useractivity__played_at",
        )

        # Calculate amount of unique artists on the period selected
        count = (
            objects
            # Group artists by ms_played
            .annotate(time_played_ms=Sum("tracks__useractivity__ms_played"))
            # Filter by those listened to more than 2 minutes (120000 ms)
            .filter(time_played_ms__gte=120000)
            # Count by unique artists
            .aggregate(Count("sp_id", distinct=True))
        )

        previous_objects = filter_model_by_date_selection_previous_period(
            Artists,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="tracks__useractivity__played_at",
        )

        previous_count = (
            previous_objects.annotate(
                time_played_ms=Sum("tracks__useractivity__ms_played")
            )
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
