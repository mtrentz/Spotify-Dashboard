from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.track_serializers import (
    TopTracksSerializer,
    UniqueTracksSerializer,
)
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from ..models import Tracks
from datetime import datetime, timedelta, timezone
from ..helpers import validate_days_query_param, validate_qty_query_params


class TopPlayedTracksView(ListAPIView):
    serializer_class = TopTracksSerializer

    def get_queryset(self):

        # How many days in the past to include, defaults to 7, func will raise for errors
        days = validate_days_query_param(self.request.query_params.get("days", 7))

        # How many artists to return, defaults to 10, func will raise for errors
        qty = validate_qty_query_params(self.request.query_params.get("qty", 10))

        date_now = datetime.now(timezone.utc)
        date_start = date_now - timedelta(days=days)

        items = (
            Tracks.objects.filter(useractivity__played_at__range=[date_start, date_now])
            .annotate(time_played_ms=Sum("useractivity__ms_played"))
            .order_by("-time_played_ms")[:qty]
        )

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
        # How many days in the past to include, defaults to 7, func will raise for errors
        days = validate_days_query_param(self.request.query_params.get("days", 7))

        date_now = datetime.now(timezone.utc)
        date_start = date_now - timedelta(days=days)

        # Calculate amount of unique tracks on the period selected
        count = (
            Tracks.objects
            # Filter by range
            .filter(useractivity__played_at__range=[date_start, date_now])
            # Group tracks by ms_played
            .annotate(time_played_ms=Sum("useractivity__ms_played"))
            # Filter by those listened to more than 2 minutes (120000 ms)
            .filter(time_played_ms__gte=120000)
            # Count by unique tracks
            .aggregate(Count("sp_id", distinct=True))
        )

        # To return the growth, calculate the unique count from the same number of days in the period just before.
        # The start of this one is at the end of the past one
        previous_date_end = date_start
        previous_date_start = previous_date_end - timedelta(days=days)

        previous_count = (
            Tracks.objects.filter(
                useractivity__played_at__range=[previous_date_start, previous_date_end]
            )
            .annotate(time_played_ms=Sum("useractivity__ms_played"))
            .filter(time_played_ms__gte=120000)
            .aggregate(Count("sp_id", distinct=True))
        )

        # Calculate the growth
        # Check if there was something listened to in the last period,
        # else set growth to 0, to avoid division by 0.
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
