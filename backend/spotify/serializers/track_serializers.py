from rest_framework import serializers


class TopTracksSerializer(serializers.Serializer):
    track = serializers.CharField(max_length=255)
    album = serializers.CharField(max_length=255)
    album_cover = serializers.URLField()
    artists = serializers.ListField(child=serializers.CharField(max_length=255))
    minutes_played = serializers.IntegerField()


class UniqueTracksSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    growth = serializers.FloatField()
