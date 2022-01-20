from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.artist_serializers import (
    TopArtistsSerializers,
    UniqueArtistsSerializer,
)
from ..models import Artists
from django.db.models import Sum, Count
from datetime import datetime, timedelta, timezone
from ..helpers import validate_days_query_param, validate_qty_query_params


class TopPlayedArtistsView(ListAPIView):
    serializer_class = TopArtistsSerializers

    def get_queryset(self):

        # How many days in the past to include, defaults to 7, func will raise for errors
        days = validate_days_query_param(self.request.query_params.get("days", 7))

        # How many artists to return, defaults to 10, func will raise for errors
        qty = validate_qty_query_params(self.request.query_params.get("qty", 10))

        date_now = datetime.now(timezone.utc)
        date_start = date_now - timedelta(days=days)

        items = (
            Artists.objects.filter(
                tracks__useractivity__played_at__range=[date_start, date_now]
            )
            .annotate(time_played_ms=Sum("tracks__useractivity__ms_played"))
            .order_by("-time_played_ms")[:qty]
        )

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
        # How many days in the past to include, defaults to 7, func will raise for errors
        days = validate_days_query_param(self.request.query_params.get("days", 7))

        date_now = datetime.now(timezone.utc)
        date_start = date_now - timedelta(days=days)

        # Calculate amount of unique artists on the period selected
        count = (
            Artists.objects
            # Filter by range
            .filter(tracks__useractivity__played_at__range=[date_start, date_now])
            # Group artists by ms_played
            .annotate(time_played_ms=Sum("tracks__useractivity__ms_played"))
            # Filter by those listened to more than 2 minutes (120000 ms)
            .filter(time_played_ms__gte=120000)
            # Count by unique artists
            .aggregate(Count("sp_id", distinct=True))
        )

        # To return the growth, calculate the unique count from the same number of days in the period just before.
        # The start of this one is at the end of the past one
        previous_date_end = date_start
        previous_date_start = previous_date_end - timedelta(days=days)

        previous_count = (
            Artists.objects.filter(
                tracks__useractivity__played_at__range=[
                    previous_date_start,
                    previous_date_end,
                ]
            )
            .annotate(time_played_ms=Sum("tracks__useractivity__ms_played"))
            .filter(time_played_ms__gte=120000)
            .aggregate(Count("sp_id", distinct=True))
        )

        # Calculate the growth
        # Check if there is something to compare, to avoid division by 0
        if previous_count["sp_id__count"]:
            growth = (
                count["sp_id__count"] - previous_count["sp_id__count"]
            ) / previous_count["sp_id__count"]
        else:
            growth = 0

        return {"count": count["sp_id__count"], "growth": growth}

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset
