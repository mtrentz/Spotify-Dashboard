from rest_framework import serializers


class SimpleUserActivitySerializer(serializers.Serializer):
    track = serializers.CharField(max_length=255)
    album = serializers.CharField(max_length=255)
    album_cover = serializers.URLField()
    artists = serializers.ListField(child=serializers.CharField(max_length=255))
    played_at = serializers.DateTimeField()
    ms_played = serializers.IntegerField()


class TopTracksSerializer(serializers.Serializer):
    track = serializers.CharField(max_length=255)
    album = serializers.CharField(max_length=255)
    album_cover = serializers.URLField()
    artists = serializers.ListField(child=serializers.CharField(max_length=255))
    minutes_played = serializers.IntegerField()


class UniqueTracksSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    growth = serializers.FloatField()


class TimePlayedDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    minutes_played = serializers.IntegerField()


class TimePlayedSerializer(serializers.Serializer):
    items = serializers.ListField(child=TimePlayedDateSerializer())
    total_minutes_played = serializers.IntegerField()
    growth = serializers.FloatField()
