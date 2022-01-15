from rest_framework.generics import ListAPIView
from ..serializers.artist_serializers import TopArtistsSerializers
from ..models import Artists
from django.db.models import Sum
from datetime import datetime, timedelta, timezone
from ..helpers.helpers import validate_days_query_param, validate_qty_query_params


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
