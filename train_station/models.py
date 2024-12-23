from geopy.distance import geodesic
from geopy.geocoders import Nominatim

from django.conf import settings
from django.db import models
from django.db.models import CASCADE


def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="train_station_v1.0")
    location = geolocator.geocode(city_name)
    return location.latitude, location.longitude


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Station(models.Model):
    name = models.CharField(max_length=255)

    @property
    def latitude(self):

        """Returns the latitude of the location based on city name.
        Coordinates returned by the `get_coordinates` function in (latitude, longitude) format."""

        coordinates = get_coordinates(self.name)
        return coordinates[0]

    @property
    def longitude(self):

        """Returns the longitude of the location based on city name.
        Coordinates returned by the `get_coordinates` function in (latitude, longitude) format."""

        coordinates = get_coordinates(self.name)
        return coordinates[1]

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=CASCADE, related_name="source_routes")
    destination = models.ForeignKey(Station, on_delete=CASCADE, related_name="destination_routes")

    @property
    def distance(self):
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


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE, related_name="journeys")
    train = models.ForeignKey(Train, on_delete=CASCADE, related_name="journeys")
    crew = models.ManyToManyField(Crew, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        departure_time = self.departure_time.strftime("%Y-%m-%d %H:%M")
        return f"{self.route.source} - {self.route.destination} ({departure_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="orders")

    def __str__(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=CASCADE, related_name="tickets")

    def __str__(self):
        return f"Cargo: {self.cargo}, Seat:{self.seat}"
