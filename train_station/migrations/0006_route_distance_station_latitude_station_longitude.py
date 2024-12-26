# Generated by Django 5.1.4 on 2024-12-26 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("train_station", "0005_crew_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="route",
            name="distance",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="station",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="station",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
    ]