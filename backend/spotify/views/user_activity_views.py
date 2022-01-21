from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.user_activity_serializers import (
    SimpleUserActivitySerializer,
    TimePlayedSerializer,
)
from ..models import UserActivity
from ..helpers import (
    validate_qty_query_params,
    validate_days_query_param,
    validate_timezone_query_params,
)
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger("django")


class RecentUserActivityView(ListAPIView):
    serializer_class = SimpleUserActivitySerializer

    def get_queryset(self):
        # How many tracks to return, defaults to 10, func will raise for errors
        qty = validate_qty_query_params(self.request.query_params.get("qty", 10))

        items = UserActivity.objects.order_by("-played_at")[:qty]

        queryset = []

        for item in items:
            queryset.append(
                {
                    "track": item.track.name,
                    "album": item.track.album.name,
                    "album_cover": item.track.album.art_sm,
                    "artists": [a.name for a in item.track.artists.all()],
                    "played_at": item.played_at,
                    "ms_played": item.ms_played,
                }
            )

        return queryset


class TimePlayedView(RetrieveAPIView):
    serializer_class = TimePlayedSerializer

    def get_queryset(self):
        """
        Here I will always return the days amount of data points.
        If the query param for days is 10, it will try to return the 10 latests days on the database.
        In case there isn't enough data, only then will return less than that amount of data points.
        """
        # TODO: Não tenho 100% de ctz que ta lidando certo com timezone pro date range
        # TODO: Utilizar Trunc() só, e deixar escolher day/week/month pra truncar.
        # Ou fazer automatico pelo numero de dias. If days > x, trunc week etc...
        # Tem que ver como o grafico do frontend lida com isso

        # How many data points to include. Defaults to 7, func will raise for errors
        days = validate_days_query_param(self.request.query_params.get("days", 7))
        # Timezone from the client request, defaults to UTC. If name invalid, also defaults to UTC
        tz_name = validate_timezone_query_params(
            self.request.query_params.get("timezone", "UTC")
        )

        tzinfo = pytz.timezone(tz_name)

        date_now = datetime.now(tzinfo)
        date_start = date_now - timedelta(days=days)

        # Here I have the amount played day by day in the current period.
        time_played_by_day = (
            UserActivity.objects
            # Filter by range
            .filter(played_at__range=[date_start, date_now])
            # Truncate by day
            .annotate(day=TruncDay("played_at", tzinfo=tzinfo))
            # Get the values for each day
            .values("day")
            # Sum the ms_played for each day
            .annotate(time_played_ms=Sum("ms_played"))
            # Order so the oldest is first
            .order_by("day")
        )

        # Sum the ms_played for the current period
        ms_played_current = time_played_by_day.aggregate(Sum("time_played_ms"))[
            "time_played_ms__sum"
        ]

        if not ms_played_current:
            ms_played_current = 0

        # To return the growth, i'll ned to do this ms_played sum in the past period
        previous_date_end = date_start
        previous_date_start = previous_date_end - timedelta(days=days)

        ms_played_previous = (
            UserActivity.objects
            # Filter by range
            .filter(played_at__range=[previous_date_start, previous_date_end])
            # Aggregate the sum
            .aggregate(Sum("ms_played"))
        )["ms_played__sum"]

        # Items is going to be a list of objects {'date': date, 'minutes_played': int}
        items = []

        for obj in time_played_by_day:
            items.append(
                {
                    "date": obj["day"].strftime("%Y-%m-%d"),
                    "minutes_played": obj["time_played_ms"] / 60_000,
                }
            )

        # In case there was no data for previous period, I will set growth to 0
        if ms_played_previous:
            growth = (ms_played_current - ms_played_previous) / ms_played_previous
        else:
            growth = 0

        queryset = {
            "items": items,
            "total_minutes_played": ms_played_current / 60_000,
            "growth": round(growth, 2),
            "tz_name": tz_name,
        }

        return queryset

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset
