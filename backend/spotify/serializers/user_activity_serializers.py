from rest_framework import serializers


class SimpleUserActivitySerializer(serializers.Serializer):
    track = serializers.CharField(max_length=255)
    album = serializers.CharField(max_length=255)
    album_cover = serializers.URLField()
    artists = serializers.ListField(child=serializers.CharField(max_length=255))
    played_at = serializers.DateTimeField()
    ms_played = serializers.IntegerField()


class AvailableYearsSerializer(serializers.Serializer):
    year = serializers.IntegerField()


class TimePlayedDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    minutes_played = serializers.IntegerField()


class TimePlayedSerializer(serializers.Serializer):
    items = serializers.ListField(child=TimePlayedDateSerializer())
    total_minutes_played = serializers.IntegerField()
    growth = serializers.FloatField()
    tz_name = serializers.CharField(max_length=255)


class FirstAndLastDayYearSerializer(serializers.Serializer):
    first_day = serializers.DateField()
    last_day = serializers.DateField()


class UserActivityStatisticsSerializer(serializers.Serializer):
    average_minutes_per_day = serializers.FloatField()
    total_time_played_in_days = serializers.FloatField()
    day_of_week_most_activity = serializers.CharField(max_length=255)
    hour_of_day_most_activity = serializers.CharField(max_length=255)
