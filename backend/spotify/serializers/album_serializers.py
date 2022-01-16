from rest_framework import serializers


class UniqueAlbumsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    growth = serializers.FloatField()
