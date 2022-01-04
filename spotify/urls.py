from django.urls import path
from .views import *

urlpatterns = [
    path("entry/", TrackEntryView.as_view(), name="entry"),
]
