from rest_framework import serializers


class TopArtistsSerializers(serializers.Serializer):
    artist = serializers.CharField(max_length=255)
    minutes_played = serializers.IntegerField()


class UniqueArtistsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    growth = serializers.FloatField()
