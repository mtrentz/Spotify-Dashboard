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

    def __str__(self):
        return self.name


class Albums(models.Model):
    sp_id = models.CharField(max_length=255, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    popularity = models.IntegerField(null=True)
    release_date = models.DateField(null=True)
    total_tracks = models.IntegerField(null=True)
    type = models.CharField(max_length=50, null=True)
    # TODO: Ver como funciona qnd um album tem varios artistas
    artists = models.ManyToManyField(Artists)

    def __str__(self):
        # TODO: Colocar nome do artista junto ao album
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


class BulkHistory(models.Model):
    end_time = models.DateTimeField(null=True)
    artist_name = models.CharField(max_length=255, null=True)
    track_name = models.CharField(max_length=255, null=True)
    ms_played = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.end_time} - {self.artist_name} - {self.track_name}"


class UserActivity(models.Model):
    # Não pode ter musica com o mesmo timestamp. Se tiver, é pq é entry repetido
    played_at = models.DateTimeField(null=True, unique=True)
    ms_played = models.IntegerField(null=True)
    from_import = models.BooleanField(null=True)
    track = models.ForeignKey(Tracks, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.played_at} - {self.track.name} - {self.ms_played}"
