from rest_framework.generics import ListAPIView
from ..serializers.artist_serializers import (
    TopArtistsSerializers,
)
from ..models import Artists
from django.db.models import Sum


class TopPlayedArtists(ListAPIView):
    serializer_class = TopArtistsSerializers

    def get_queryset(self):
        # TODO: Catch error range
        items = Artists.objects.annotate(
            time_played=Sum("tracks__useractivity__ms_played")
        ).order_by("-time_played")[:10]
        queryset = []
        for item in items:
            queryset.append(
                {
                    "artist": item.name,
                    "minutes_played": item.time_played / 60_000,
                }
            )

        return queryset
