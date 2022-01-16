# Generated by Django 4.0.1 on 2022-01-16 00:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Albums',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sp_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('popularity', models.IntegerField(null=True)),
                ('release_date', models.DateField(null=True)),
                ('total_tracks', models.IntegerField(null=True)),
                ('type', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Artists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sp_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('popularity', models.IntegerField(null=True)),
                ('followers', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genres',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tracks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sp_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('duration', models.IntegerField(null=True)),
                ('popularity', models.IntegerField(null=True)),
                ('explicit', models.BooleanField(null=True)),
                ('track_number', models.IntegerField(null=True)),
                ('disc_number', models.IntegerField(null=True)),
                ('type', models.CharField(max_length=50, null=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spotify.albums')),
                ('artists', models.ManyToManyField(to='spotify.Artists')),
            ],
        ),
        migrations.CreateModel(
            name='StreamingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('end_time', models.DateTimeField()),
                ('artist_name', models.CharField(max_length=255)),
                ('track_name', models.CharField(max_length=255)),
                ('ms_played', models.IntegerField()),
            ],
            options={
                'unique_together': {('end_time', 'artist_name', 'track_name', 'ms_played')},
            },
        ),
        migrations.AddField(
            model_name='artists',
            name='genres',
            field=models.ManyToManyField(to='spotify.Genres'),
        ),
        migrations.AddField(
            model_name='albums',
            name='artists',
            field=models.ManyToManyField(to='spotify.Artists'),
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played_at', models.DateTimeField(null=True)),
                ('ms_played', models.IntegerField(null=True)),
                ('from_import', models.BooleanField(null=True)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spotify.tracks')),
            ],
            options={
                'unique_together': {('played_at', 'ms_played', 'from_import', 'track')},
            },
        ),
    ]
