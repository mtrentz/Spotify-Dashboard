from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from spotify.models import Genres, Artists, Albums, Tracks
from django.db import IntegrityError


class TestModels(APITestCase):
    def setUp(self):
        user = User.objects.create_superuser('admin', 'admin@admin.com', "admin")
        self.client.force_authenticate(user)

        self.genres = ["rock", "rap", "pop"]
        self.artists_one = {
            "sp_id": "FAKEdsad7sa8d7sa89DAS",
            "name": "Led Zeppelin",
            "popularity": 100,
        }
        self.artist_two = {
            "sp_id": "FAKEdsad7sa8d7as67821",
            "name": "Pink Floyd",
            "popularity": 100,
        }
        self.album_one = {
            "sp_id": "FAKEdsadas78123718237821dsadsa",
            "name": "Led Zeppelin IV",
        }
        self.album_two = {
            "sp_id": "FAKEdsadas7831273821sdasD",
            "name": "The Wall",
        }
        self.track_one = {
            "sp_id": "FAKEdasdsa8778dasDSA789da",
            "name": "Stairway to Heaven",
            "duration": 300,
        }
        self.track_two = {
            "sp_id": "FAKEdsa891283721dsa7981",
            "name": "Black Dog",
            "duration": 500,
        }

    def test_constraints(self):
        _ = Genres.objects.create(name=self.genres[0])

        # Test unique constraint, very simple, just to figure out syntax of doing it
        with self.assertRaises(IntegrityError):
            _ = Genres.objects.create(name=self.genres[0])

    def test_relationships(self):
        # Create genres
        rock = Genres.objects.create(name=self.genres[0])
        rap = Genres.objects.create(name=self.genres[1])
        pop = Genres.objects.create(name=self.genres[2])

        # Create artist one genre
        artist_one = Artists.objects.create(**self.artists_one)
        artist_one.genres.add(rock)

        self.assertEquals(artist_one.genres.count(), 1)
        self.assertEquals(artist_one.genres.first().name, "rock")

        # Create artist with more genres
        artist_two = Artists.objects.create(**self.artist_two)
        artist_two.genres.add(rock)
        artist_two.genres.add(rap)
        artist_two.genres.add(pop)

        self.assertEquals(artist_two.genres.count(), 3)

        # Try to add same again, should still be 3
        artist_two.genres.add(rock)
        self.assertEquals(artist_two.genres.count(), 3)

        # Create album one artist
        album_one = Albums.objects.create(**self.album_one)
        album_one.artists.add(artist_one)

        self.assertEquals(album_one.artists.count(), 1)
        self.assertEquals(album_one.artists.first().name, "Led Zeppelin")

        # Create album two artist
        album_two = Albums.objects.create(**self.album_two)
        album_two.artists.add(artist_one)
        album_two.artists.add(artist_two)

        self.assertEquals(album_two.artists.count(), 2)

        # Create track with two artist, and album
        track_one = Tracks.objects.create(album=album_one, **self.track_one)
        track_one.artists.add(artist_one)
        track_one.artists.add(artist_two)

        self.assertEquals(track_one.artists.count(), 2)
        self.assertEquals(track_one.album.name, "Led Zeppelin IV")

        # Create track with no album, check for error
        with self.assertRaises(IntegrityError):
            _ = Tracks.objects.create(**self.track_two)
