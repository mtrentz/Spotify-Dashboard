from django.urls import path
from .views.insert_views import *

urlpatterns = [
    path("entry/", TrackEntryView.as_view(), name="entry"),
    path("history/", ImportStreamingHistoryView.as_view(), name="history"),
]
