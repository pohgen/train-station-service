import os
import time
import uuid

from django.core.exceptions import ValidationError
from django.utils.text import slugify
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

from django.conf import settings
from django.db import models
from django.db.models import CASCADE


def get_coordinates(city_name):
    for attempt in range(5):
        try:
            geolocator = Nominatim(user_agent="train_station_v1.0")
            location = geolocator.geocode(city_name)
            return location.latitude, location.longitude
        except GeocoderTimedOut as error:
            print(f"Geocoder timed out again: {error}")
            if attempt < 5:
                time.sleep(0.5)


def crew_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.last_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/staff/", filename)


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=crew_image_file_path)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.latitude:
            self.latitude = self.calculate_latitude()
        if not self.longitude:
            self.longitude = self.calculate_longitude()
        super(Station, self).save(*args, **kwargs)

    def calculate_latitude(self):

        """Returns the latitude of the location based on city name.
        Coordinates returned by the `get_coordinates` function in (latitude, longitude) format."""

        coordinates = get_coordinates(self.name)
        return coordinates[0]

    def calculate_longitude(self):

        """Returns the longitude of the location based on city name.
        Coordinates returned by the `get_coordinates` function in (latitude, longitude) format."""

        coordinates = get_coordinates(self.name)
        return coordinates[1]

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=CASCADE, related_name="source_routes")
    destination = models.ForeignKey(Station, on_delete=CASCADE, related_name="destination_routes")
    distance = models.IntegerField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.distance:
            self.distance = self.calculate_distance()
        super(Route, self).save(*args, **kwargs)

    def calculate_distance(self):
        """
        Returns the integer distance of 2 cities based on their name.
        Coordinates returned by the `get_coordinates` and counted kilometers by 'geodesic'
        """
        coord_source = get_coordinates(self.source.name)
        coord_destination = get_coordinates(self.destination.name)
        distance = geodesic(coord_source, coord_destination).kilometers
        return int(distance)

    def __str__(self):
        return f"{self.source} - {self.destination}"

    class Meta:
        unique_together = ("source", "destination")


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=CASCADE, related_name="trains")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE, related_name="journeys")
    train = models.ForeignKey(Train, on_delete=CASCADE, related_name="journeys")
    crew = models.ManyToManyField(Crew, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        departure_time = self.departure_time.strftime("%Y-%m-%d %H:%M")
        return f"{self.route.source} - {self.route.destination} ({departure_time})"

    class Meta:
        ordering = ["-departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="orders")

    def __str__(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"Cargo: {self.cargo}, Seat:{self.seat}"

    class Meta:
        unique_together = ("cargo", "seat", "journey")
