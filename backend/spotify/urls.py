from django.urls import path
from .views.insert_views import (
    TrackEntryView,
    ImportStreamingHistoryView,
)
from .views.track_views import (
    RecentUserActivityView,
    TopPlayedTracksView,
    UniqueTracksView,
    TimePlayedView,
)
from .views.artist_views import TopPlayedArtistsView, UniqueArtistsView
from .views.album_views import UniqueAlbumsViews
from .views.auth_views import AuthURLView, AuthTokenView

urlpatterns = [
    # Inserting Data
    path("entry/", TrackEntryView.as_view(), name="entry"),
    path("history/", ImportStreamingHistoryView.as_view(), name="history"),
    # Auth
    path("auth/", AuthURLView.as_view(), name="auth_url"),
    path("token/", AuthTokenView.as_view(), name="auth_token"),
    # Query
    path("recently-played/", RecentUserActivityView.as_view(), name="recently_played"),
    path(
        "top-played-artists/", TopPlayedArtistsView.as_view(), name="top_played_artists"
    ),
    path("top-played-tracks/", TopPlayedTracksView.as_view(), name="top_played_tracks"),
    path("unique-artists/", UniqueArtistsView.as_view(), name="unique_artists"),
    path("unique-tracks/", UniqueTracksView.as_view(), name="unique_tracks"),
    path("unique-albums/", UniqueAlbumsViews.as_view(), name="unique_albums"),
    path("time-played/", TimePlayedView.as_view(), name="time_played"),
]
