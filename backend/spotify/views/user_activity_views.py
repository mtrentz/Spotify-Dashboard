from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.user_activity_serializers import (
    SimpleUserActivitySerializer,
    TimePlayedSerializer,
)
from ..models import UserActivity
from ..helpers import validate_qty_query_params, validate_days_query_param
from django.db.models import Sum
from django.db.models.functions import TruncDay


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
        # TODO: Talvez tenha que lidar diferente com a timezone aqui

        # How many data points to include. Defaults to 7, func will raise for errors
        days = validate_days_query_param(self.request.query_params.get("days", 7))

        time_played_by_day = (
            UserActivity.objects
            # Truncate by day
            .annotate(day=TruncDay("played_at"))
            # Get the values for each day
            .values("day")
            # Sum the ms_played for each day
            .annotate(time_played_ms=Sum("ms_played"))
            # Order so the newest is first
            .order_by("-day")
            # Limit to the amount of days requested times two (so I can compare to previous period)
            [: days * 2]
        )
        # Here I will invert the data, so the newest is last (order of graph used in frontend)
        time_played_by_day = time_played_by_day[::-1]

        # Items is going to be a list of objects {'date': date, 'minutes_played': int}
        all_items = []

        for obj in time_played_by_day:
            all_items.append(
                {
                    "date": obj["day"].strftime("%Y-%m-%d"),
                    "minutes_played": obj["time_played_ms"] / 60_000,
                }
            )

        # Now I want to separate the items in two lists, one for the current period (most recent) and one for the previous one, for comparison.
        # The most recent data is at the end of the list
        current_items = all_items[-days:]
        previous_items = all_items[:-days]

        # Now getting the total minutes played of the current period
        total_minutes_played = sum([item["minutes_played"] for item in current_items])

        # To calculate the growth, I will sum the minutes played of the previous period
        previous_total_minutes_played = sum(
            [item["minutes_played"] for item in previous_items]
        )

        # In case there was no data for previous period, I will set growth to 0
        if previous_total_minutes_played:
            growth = (
                total_minutes_played - previous_total_minutes_played
            ) / previous_total_minutes_played
        else:
            growth = 0

        queryset = {
            "items": current_items,
            "total_minutes_played": total_minutes_played,
            "growth": round(growth, 2),
        }

        return queryset

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
        return queryset
