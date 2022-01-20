from django.db import models

# Create your models here.


class Genres(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.name


class Artists(models.Model):
    sp_id = models.CharField(max_length=255, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    popularity = models.IntegerField(null=True)
    followers = models.IntegerField(null=True)
    genres = models.ManyToManyField(Genres)
    art_sm = models.URLField(null=True)
    art_md = models.URLField(null=True)
    art_lg = models.URLField(null=True)

    def __str__(self):
        return self.name


class Albums(models.Model):
    sp_id = models.CharField(max_length=255, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    popularity = models.IntegerField(null=True)
    release_date = models.DateField(null=True)
    total_tracks = models.IntegerField(null=True)
    type = models.CharField(max_length=50, null=True)
    artists = models.ManyToManyField(Artists)
    art_sm = models.URLField(null=True)
    art_md = models.URLField(null=True)
    art_lg = models.URLField(null=True)

    def __str__(self):
        return self.name


class Tracks(models.Model):
    sp_id = models.CharField(max_length=255, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    duration = models.IntegerField(null=True)
    popularity = models.IntegerField(null=True)
    explicit = models.BooleanField(null=True)
    track_number = models.IntegerField(null=True)
    disc_number = models.IntegerField(null=True)
    type = models.CharField(max_length=50, null=True)
    album = models.ForeignKey(Albums, on_delete=models.CASCADE)
    artists = models.ManyToManyField(Artists)

    def __str__(self):
        return self.name


class StreamingHistory(models.Model):
    end_time = models.DateTimeField(null=False)
    artist_name = models.CharField(max_length=255, null=False)
    track_name = models.CharField(max_length=255, null=False)
    ms_played = models.IntegerField(null=False)

    class Meta:
        unique_together = ("end_time", "artist_name", "track_name", "ms_played")

    def __str__(self):
        return f"{self.end_time} - {self.artist_name} - {self.track_name}"


class UserActivity(models.Model):
    # Não pode ter musica com o mesmo timestamp. Se tiver, é pq é entry repetido
    played_at = models.DateTimeField(null=True)
    ms_played = models.IntegerField(null=True)
    from_import = models.BooleanField(null=True)
    track = models.ForeignKey(Tracks, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("played_at", "ms_played", "from_import", "track")

    def __str__(self):
        return f"{self.played_at.strftime('%Y-%m-%d %H:%M:%S')} - {self.track.name} - {self.ms_played}"


class SearchHistory(models.Model):
    """
    This is a very basic model to correlate the track and artist name that
    came from Spotify's history with the track that was found after using the search api.

    The reason that this is needed is that sometimes, on spotify's history, there will be tracks like:
    'The Rover - Remaster 2010', but when I try searching for it, to get the track ID and all other info,
    I either don't find it and have to search without the Remaster, or find another version!

    So to avoid searching for the same names again, I will just store the query parameters and the track ID
    that I was able to find.
    """

    track_name = models.CharField(max_length=255, null=False)
    artist_name = models.CharField(max_length=255, null=False)
    track_sp_id = models.CharField(max_length=255, null=True)
