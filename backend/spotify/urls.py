from django.urls import path
from .views.insert_views import (
    TrackEntryView,
    ImportStreamingHistoryView,
)
from .views.track_views import RecentUserActivityView
from .views.auth_views import AuthURLView, AuthTokenView

urlpatterns = [
    # Inserting Data
    path("entry/", TrackEntryView.as_view(), name="entry"),
    path("history/", ImportStreamingHistoryView.as_view(), name="history"),
    # Auth
    path("auth/", AuthURLView.as_view(), name="auth_url"),
    path("token/", AuthTokenView.as_view(), name="auth_token"),
    # Query Tracks
    path("recent/", RecentUserActivityView.as_view(), name="recent"),
]
