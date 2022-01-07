from rest_framework import serializers
from .models import *
from .helpers import insert_user_activity
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from dotenv import load_dotenv
import pytz


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = "__all__"


class ArtistsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artists
        fields = "__all__"


class AlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Albums
        fields = "__all__"


class TracksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracks
        fields = "__all__"


class StreamingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingHistory
        fields = "__all__"


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = "__all__"


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

    load_dotenv()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

    def save(self):
        validated_data = self.validated_data

        ### ARTISTS
        artists_sp_ids = validated_data["artists_sp_ids"]
        artists = []
        for artist_sp_id in artists_sp_ids:
            # First check if artist already exists in database
            artist = Artists.objects.filter(sp_id=artist_sp_id).first()
            # If exists
            if artist:
                # Just append it to list and continue to next iteration
                artists.append(artist)
                continue

            artist_response = self.sp.artist(artist_sp_id)
            artist_name = artist_response.get("name")
            artist_popularity = artist_response.get("popularity")
            artist_followers = artist_response.get("followers").get("total")

            artist, _ = Artists.objects.get_or_create(
                sp_id=artist_sp_id,
                name=artist_name,
                popularity=artist_popularity,
                followers=artist_followers,
            )
            artist.save()
            artists.append(artist)

            genres = artist_response.get("genres")
            # Add genres to database
            for genre in genres:
                genre, _ = Genres.objects.get_or_create(name=genre)
                artist.genres.add(genre)

        ### ALBUM
        album_sp_id = validated_data["album_sp_id"]

        # First check if album already exists in database
        album = Albums.objects.filter(sp_id=album_sp_id).first()
        # If not exist, query it from Spotify, and save it
        if not album:
            album_response = self.sp.album(album_sp_id)
            album_name = album_response.get("name")
            album_popularity = album_response.get("popularity")
            album_total_tracks = album_response.get("total_tracks")
            album_type = album_response.get("album_type")

            album_release_date = album_response.get("release_date")
            album_release_date_precision = album_response.get("release_date_precision")

            if album_release_date_precision == "year":
                album_release_date = datetime.strptime(album_release_date, "%Y")
            elif album_release_date_precision == "month":
                album_release_date = datetime.strptime(album_release_date, "%Y-%m")
            else:
                album_release_date = datetime.strptime(album_release_date, "%Y-%m-%d")

            album, _ = Albums.objects.get_or_create(
                sp_id=album_sp_id,
                name=album_name,
                popularity=album_popularity,
                release_date=album_release_date,
                total_tracks=album_total_tracks,
                type=album_type,
            )
            album.save()

            # Add artists to album (many to many)
            album.artists.add(*artists)

        ### TRACK
        # Here I don't have to query spotify, since I already have all the info I need
        track_sp_id = validated_data["track_sp_id"]
        track_name = validated_data["track_name"]
        track_duration = validated_data["track_duration"]
        track_popularity = validated_data["track_popularity"]
        track_explicit = validated_data["track_explicit"]
        track_number = validated_data["track_number"]
        track_disc_number = validated_data["track_disc_number"]
        track_type = validated_data["track_type"]

        track, _ = Tracks.objects.get_or_create(
            sp_id=track_sp_id,
            name=track_name,
            duration=track_duration,
            popularity=track_popularity,
            explicit=track_explicit,
            track_number=track_number,
            disc_number=track_disc_number,
            type=track_type,
            album=album,
        )
        track.save()
        track.artists.add(*artists)

        ### User Activity
        played_at = validated_data["played_at"]
        ms_played = validated_data["ms_played"]
        from_import = validated_data["from_import"]

        # Here I will check if need to add to user activity.
        # There are some extra considerations to be made, which will be explained in the function
        insert_user_activity(
            track=track,
            played_at=played_at,
            ms_played=ms_played,
            from_import=from_import,
        )
