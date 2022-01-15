from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ParseError
from ..serializers.artist_serializers import (
    TopArtistsSerializers,
)
from ..models import Artists
from django.db.models import Sum


class TopPlayedArtists(ListAPIView):
    serializer_class = TopArtistsSerializers

    def get_queryset(self):

        # Defaults to 10
        try:
            qty = int(self.request.query_params.get("qty", 10))
        except ValueError:
            raise ParseError("qty must be an integer")
        if qty < 0:
            raise ParseError("qty must be positive")
        if qty > 50:
            raise ParseError("qty must be less than 50")

        items = Artists.objects.annotate(
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
