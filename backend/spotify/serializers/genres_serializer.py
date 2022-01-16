from rest_framework import serializers


class TopPlayedGenreSerializer(serializers.Serializer):
    genre = serializers.CharField(max_length=255)
    minutes_played = serializers.IntegerField()
