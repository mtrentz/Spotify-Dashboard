from django.urls import path
from .views.insert_views import (
    RecentlyPlayedView,
    TrackEntryView,
    ImportStreamingHistoryView,
)
from .views.auth_views import AuthURLView, AuthTokenView

urlpatterns = [
    path("entry/", TrackEntryView.as_view(), name="entry"),
    path("history/", ImportStreamingHistoryView.as_view(), name="history"),
    path("auth/", AuthURLView.as_view(), name="auth_url"),
    path("token/", AuthTokenView.as_view(), name="auth_token"),
]
