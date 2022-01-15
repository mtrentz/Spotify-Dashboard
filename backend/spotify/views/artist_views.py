from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ParseError
from ..serializers.artist_serializers import (
    TopArtistsSerializers,
)
from ..models import Artists
from django.db.models import Sum
from datetime import datetime, timedelta, tzinfo
import pytz


class TopPlayedArtists(ListAPIView):
    serializer_class = TopArtistsSerializers

    def get_queryset(self):

        # How many days in the past to include, defaults to 7
        try:
            days = int(self.request.query_params.get("days", 7))
        except ValueError:
            raise ParseError("days must be an integer")
        if days < 0:
            raise ParseError("days must be positive")

        # Amount of data to return. Defaults to 10
        try:
            qty = int(self.request.query_params.get("qty", 10))
        except ValueError:
            raise ParseError("qty must be an integer")
        if qty < 0:
            raise ParseError("qty must be positive")
        if qty > 50:
            raise ParseError("qty must be less than 50")

        date_now = datetime.utcnow()
        date_start = date_now - timedelta(days=days)
        print(date_start)

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
