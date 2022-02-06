from rest_framework import serializers


class UniqueAlbumsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    growth = serializers.FloatField()


class TopAlbumsSerializers(serializers.Serializer):
    album = serializers.CharField(max_length=255)
    album_cover = serializers.URLField()
    artists = serializers.ListField(child=serializers.CharField(max_length=255))
    minutes_played = serializers.IntegerField()
