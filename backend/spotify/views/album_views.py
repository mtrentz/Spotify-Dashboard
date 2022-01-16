from rest_framework.generics import RetrieveAPIView
from ..models import Albums
from ..serializers.album_serializers import UniqueAlbumsSerializer
from django.db.models import Sum, Count
from datetime import datetime, timedelta, timezone
from ..helpers.helpers import validate_days_query_param


class UniqueAlbumsViews(RetrieveAPIView):
    serializer_class = UniqueAlbumsSerializer

    def get_queryset(self):
        # How many days in the past to include, defaults to 7, func will raise for errors
        days = validate_days_query_param(self.request.query_params.get("days", 7))

        date_now = datetime.now(timezone.utc)
        date_start = date_now - timedelta(days=days)

        # Calculate amount of unique albums on the period selected
        count = (
            Albums.objects
            # Filter by range
            .filter(tracks__useractivity__played_at__range=[date_start, date_now])
            # Group albums by ms_played
            .annotate(time_played_ms=Sum("tracks__useractivity__ms_played"))
            # Filter by those listened to more than 2 minutes (120000 ms)
            .filter(time_played_ms__gte=120000)
            # Count by unique albums
            .aggregate(Count("sp_id", distinct=True))
        )

        # To return the growth, calculate the unique count from the same number of days in the period just before.
        # The start of this one is at the end of the past one
        previous_date_end = date_start
        previous_date_start = previous_date_end - timedelta(days=days)

        previous_count = (
            Albums.objects.filter(
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
        growth = (
            count["sp_id__count"] - previous_count["sp_id__count"]
        ) / previous_count["sp_id__count"]

        return {"count": count["sp_id__count"], "growth": growth}

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset
