from django.urls import path
from .views.insert_views import ImportStreamingHistoryView, RecentlyPlayedView
from .views.track_views import TopPlayedTracksView, UniqueTracksView
from .views.user_activity_views import RecentUserActivityView, TimePlayedView
from .views.artist_views import TopPlayedArtistsView, UniqueArtistsView
from .views.album_views import UniqueAlbumsViews
from .views.genres_views import TopPlayedGenresView
from .views.auth_views import AuthURLView, AuthTokenView

urlpatterns = [
    # INSERT DATA
    path("history/", ImportStreamingHistoryView.as_view(), name="history"),
    path(
        "refresh-recently-played/",
        RecentlyPlayedView.as_view(),
        name="refresh-recently-played",
    ),
    # AUTHORIZATION
    path("auth/", AuthURLView.as_view(), name="auth_url"),
    path("token/", AuthTokenView.as_view(), name="auth_token"),
    # USER ACTIVITY
    path("recently-played/", RecentUserActivityView.as_view(), name="recently_played"),
    path("time-played/", TimePlayedView.as_view(), name="time_played"),
    # ARTISTS
    path("unique-artists/", UniqueArtistsView.as_view(), name="unique_artists"),
    path(
        "top-played-artists/", TopPlayedArtistsView.as_view(), name="top_played_artists"
    ),
    # TRACKS
    path("unique-tracks/", UniqueTracksView.as_view(), name="unique_tracks"),
    path("top-played-tracks/", TopPlayedTracksView.as_view(), name="top_played_tracks"),
    # ALBUMS
    path("unique-albums/", UniqueAlbumsViews.as_view(), name="unique_albums"),
    path("top-played-genres/", TopPlayedGenresView.as_view(), name="top_played_genres"),
]
