from rest_framework.generics import ListAPIView
from ..serializers.track_serializers import (
    SimpleUserActivitySerializer,
)
from ..models import UserActivity


class RecentUserActivityView(ListAPIView):
    serializer_class = SimpleUserActivitySerializer

    def get_queryset(self):
        items = UserActivity.objects.order_by("-played_at")[:10]
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
