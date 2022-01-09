# Generated by Django 4.0.1 on 2022-01-08 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyAuthorizationTokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('expires_in', models.IntegerField()),
                ('expires_at', models.IntegerField()),
                ('scope', models.CharField(max_length=255)),
                ('token_type', models.CharField(max_length=255)),
            ],
        ),
    ]