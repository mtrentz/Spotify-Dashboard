from rest_framework.generics import ListAPIView, RetrieveAPIView
from ..serializers.track_serializers import (
    SimpleUserActivitySerializer,
    TopTracksSerializer,
    UniqueTracksSerializer,
    TimePlayedSerializer,
)
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from ..models import UserActivity, Tracks
from datetime import datetime, timedelta, timezone
from ..helpers.helpers import validate_days_query_param, validate_qty_query_params


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
                    "album_cover": item.track.album.album_cover_64,
                    "artists": [a.name for a in item.track.artists.all()],
                    "played_at": item.played_at,
                    "ms_played": item.ms_played,
                }
            )

        return queryset


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
                    "album_cover": item.album.album_cover_64,
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
        growth = (
            count["sp_id__count"] - previous_count["sp_id__count"]
        ) / previous_count["sp_id__count"]

        return {"count": count["sp_id__count"], "growth": growth}

    def get_object(self):
        # Overrides the method that requires a pk
        queryset = self.get_queryset()
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
        growth = (
            total_minutes_played - previous_total_minutes_played
        ) / previous_total_minutes_played

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
