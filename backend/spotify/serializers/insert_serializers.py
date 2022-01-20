from rest_framework import serializers
from ..models import *
import pytz


# This is to verify that its a valid file
class HistoryFileSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=100, allow_empty_file=False)


class HistoryEntrySerializer(serializers.Serializer):
    # Names are different here since it's from the history file
    endTime = serializers.DateTimeField()
    artistName = serializers.CharField(max_length=255)
    trackName = serializers.CharField(max_length=255)
    msPlayed = serializers.IntegerField()

    def save(self):
        validated_data = self.validated_data
        end_time = validated_data["endTime"]

        # Sets date to UTC if not already
        if not end_time.tzinfo:
            end_time = end_time.replace(tzinfo=pytz.UTC)

        artist_name = validated_data["artistName"]
        track_name = validated_data["trackName"]
        ms_played = validated_data["msPlayed"]

        # Save if not already in StreamingHistory, save it
        if not StreamingHistory.objects.filter(
            artist_name=artist_name,
            track_name=track_name,
            ms_played=ms_played,
            end_time=end_time,
        ).exists():
            streaming_history = StreamingHistory(
                artist_name=artist_name,
                track_name=track_name,
                ms_played=ms_played,
                end_time=end_time,
            )
            streaming_history.save()


class TrackEntrySerializer(serializers.Serializer):
    # Info to query Spotify API for complete data
    album_sp_id = serializers.CharField(max_length=255, required=True)
    artists_sp_ids = serializers.ListField(
        child=serializers.CharField(max_length=255), required=True
    )

    # Track data
    track_sp_id = serializers.CharField(max_length=255, required=True)
    track_name = serializers.CharField(max_length=255, required=True)
    track_duration = serializers.IntegerField(required=False)
    track_popularity = serializers.IntegerField(required=False)
    track_explicit = serializers.BooleanField(required=False)
    track_number = serializers.IntegerField(required=False)
    track_disc_number = serializers.IntegerField(required=False)
    track_type = serializers.CharField(max_length=50, required=False)

    # Info to insert user activity
    played_at = serializers.DateTimeField(required=True)
    ms_played = serializers.IntegerField(required=True)
    from_import = serializers.BooleanField(required=True)
