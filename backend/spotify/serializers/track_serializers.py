from rest_framework import serializers


class SimpleUserActivitySerializer(serializers.Serializer):
    track = serializers.CharField(max_length=255)
    album = serializers.CharField(max_length=255)
    artists = serializers.ListField(child=serializers.CharField(max_length=255))
    played_at = serializers.DateTimeField()
    ms_played = serializers.IntegerField()
