# Generated by Django 4.0.1 on 2022-01-08 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0002_spotifyauthorizationtokens'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifyauthorizationtokens',
            name='scope',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
