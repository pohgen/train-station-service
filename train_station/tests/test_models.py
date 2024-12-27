from django.core.exceptions import ValidationError

from train_station.models import Ticket
from train_station.tests.test_factories import (
    BaseTestCase,
    sample_station,
    sample_route,
)


class StationModelTest(BaseTestCase):
    def test_latitude_and_longitude_func(self):
        station = sample_station(name="Kyiv")
        self.assertEqual(station.longitude, 30.5241361)
        self.assertEqual(station.latitude, 50.4500336)


class RouteModelTest(BaseTestCase):
    def test_distance_property(self):
        station1 = sample_station(name="Kyiv")
        station2 = sample_station(name="Paris")
        route = sample_route(source=station1, destination=station2)
        self.assertEqual(route.distance, 2031)


class TicketModelTest(BaseTestCase):

    def test_ticket_create_wrong_cargo(self):
        ticket = Ticket(cargo=123, seat=1, journey=self.journey, order=self.order)
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_ticket_create_wrong_seat(self):
        ticket = Ticket(cargo=1, seat=123, journey=self.journey, order=self.order)
        with self.assertRaises(ValidationError):
            ticket.full_clean()
