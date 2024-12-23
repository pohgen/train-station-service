from geopy.geocoders import Nominatim

from django.conf import settings
from django.db import models
from django.db.models import CASCADE


def find_lat_and_lng_by_name(name):
    geolocator = Nominatim(user_agent="train_station_v1.0")
    location = geolocator.geocode(name)
    return {
        "latitude": location.latitude,
        "longitude": location.longitude
    }


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)



class Station(models.Model):
    name = models.CharField(max_length=255)

    @property
    def latitude(self):
        coordinates = find_lat_and_lng_by_name(self.name)
        return coordinates.get("latitude")

    @property
    def longitude(self):
        coordinates = find_lat_and_lng_by_name(self.name)
        return coordinates.get("longitude")


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=CASCADE, related_name="routes")
    destination = models.ForeignKey(Station, on_delete=CASCADE, related_name="routes")
    distance = models.IntegerField()


class TrainType(models.Model):
    name = models.CharField(max_length=255)


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=CASCADE, related_name="trains")


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE, related_name="journeys")
    train = models.ForeignKey(Train, on_delete=CASCADE, related_name="journeys")
    crew = models.ManyToManyField(Crew, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="orders")


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=CASCADE, related_name="tickets")