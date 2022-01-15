from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ParseError
from ..serializers.track_serializers import (
    SimpleUserActivitySerializer,
)
from ..models import UserActivity


class RecentUserActivityView(ListAPIView):
    serializer_class = SimpleUserActivitySerializer

    def get_queryset(self):
        # Amount of data to return. Defaults to 10
        try:
            qty = int(self.request.query_params.get("qty", 10))
        except ValueError:
            raise ParseError("qty must be an integer")
        if qty < 0:
            raise ParseError("qty must be positive")
        if qty > 50:
            raise ParseError("qty must be less than 50")

        items = UserActivity.objects.order_by("-played_at")[:qty]

        queryset = []

        for item in items:
            queryset.append(
                {
                    "track": item.track.name,
                    "album": item.track.album.name,
                    "artists": [a.name for a in item.track.artists.all()],
                    "played_at": item.played_at,
                    "ms_played": item.ms_played,
                }
            )

        return queryset
