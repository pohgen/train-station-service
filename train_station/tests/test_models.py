from django.test import TestCase

from train_station.models import Station, Route


class StationModelTest(TestCase):
    def test_latitude_and_longitude_property(self):
        station = Station(name="Kyiv")
        self.assertEqual(station.longitude, 30.5241361)
        self.assertEqual(station.latitude, 50.4500336)


class RouteModelTest(TestCase):
    def test_distance_property(self):
        station1 = Station(name="Kyiv")
        station2 = Station(name="Paris")
        route = Route(source=station1, destination=station2)
        self.assertEqual(route.distance, 2031)
