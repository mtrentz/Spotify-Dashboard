from rest_framework.generics import ListAPIView
from django.db.models import Sum
from ..serializers.genres_serializer import TopPlayedGenreSerializer
from ..models import Genres
from datetime import datetime, timedelta, timezone
from ..helpers import validate_days_query_param, validate_qty_query_params


# class TopPlayedGenresView(ListAPIView):
#     serializer_class = TopPlayedGenreSerializer

#     # TODO: This is still not ready for use. Gotta figure out a way to cluster similar genres
#     # and to properly separate by artists.
#     def get_queryset(self):

#         # How many days in the past to include, defaults to 7, func will raise for errors
#         days = validate_days_query_param(self.request.query_params.get("days", 7))

#         # How many genres to return, defaults to 10, func will raise for errors
#         qty = validate_qty_query_params(self.request.query_params.get("qty", 10))

#         date_now = datetime.now(timezone.utc)
#         date_start = date_now - timedelta(days=days)

#         # TODO: This is still kinda wrong. One artist has many genres. The genres of the artists I've most listened to
#         # are going to be counted many times.
#         items = (
#             Genres.objects.filter(
#                 artists__tracks__useractivity__played_at__range=[date_start, date_now]
#             )
#             .annotate(time_played_ms=Sum("artists__tracks__useractivity__ms_played"))
#             .order_by("-time_played_ms")[:qty]
#         )

#         queryset = []

#         for item in items:
#             queryset.append(
#                 {
#                     "genre": item.name,
#                     "minutes_played": item.time_played_ms / 60_000,
#                 }
#             )

#         return queryset
