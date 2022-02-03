from rest_framework.generics import RetrieveAPIView
from ..models import Albums
from ..serializers.album_serializers import UniqueAlbumsSerializer
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


class UniqueAlbumsViews(RetrieveAPIView):
    serializer_class = UniqueAlbumsSerializer

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
            Albums,
            tzinfo,
            days_param,
            year_param,
            date_start_param,
            date_end_param,
            method,
            path_to_played_at="tracks__useractivity__played_at",
        )

        count = (
            objects
            # Group albums by ms_played
            .annotate(time_played_ms=Sum("tracks__useractivity__ms_played"))
            # Filter by those listened to more than 2 minutes (120000 ms)
            .filter(time_played_ms__gte=120000)
            # Count by unique albums
            .aggregate(Count("sp_id", distinct=True))
        )

        previous_objects = filter_model_by_date_selection_previous_period(
            Albums,
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
