from django.test import TestCase

from train_station.models import Station


class StationModelTest(TestCase):
    def test_latitude_and_longitude_property(self):
        station = Station(name="Kyiv")
        self.assertEqual(station.longitude, 30.5241361)
        self.assertEqual(station.latitude, 50.4500336)