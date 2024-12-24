from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import Station, Route, Train, TrainType, Journey, Crew, Order, Ticket
from user.models import User


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


class TicketModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="admin", password="password123")
        self.train_type = TrainType.objects.create(name="Econom")
        self.train = Train.objects.create(
            name="79-002",
            cargo_num=12,
            places_in_cargo=60,
            train_type=self.train_type
        )
        self.crew = Crew.objects.create(first_name="Nikita", last_name="Tkachenko")
        self.station1 = Station.objects.create(name="Kyiv")
        self.station2 = Station.objects.create(name="Kyiv")
        self.route = Route.objects.create(source=self.station1, destination=self.station2)
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=timezone.now() + timedelta(hours=2),
            arrival_time=timezone.now() + timedelta(hours=5)
        )
        self.journey.crew.add(self.crew,)
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            cargo=6,
            seat=1,
            journey=self.journey,
            order=self.order
        )


    def test_ticket_create_wrong_cargo(self):
        ticket = Ticket(
            cargo=123,
            seat=1,
            journey=self.journey,
            order=self.order
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_ticket_create_wrong_seat(self):
        ticket = Ticket(
            cargo=1,
            seat=123,
            journey=self.journey,
            order=self.order
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()

