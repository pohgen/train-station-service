from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import TrainType, Train, Crew, Station, Route, Journey, Order, Ticket
from user.models import User


class TicketSerializerTest(TestCase):
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

    def test_ticket_create_already_exist(self):
        payload = {
            "cargo": 6,
            "seat": 1,
            "journey": self.journey.id,
            "order": self.order.id

        }
        response = self.client.post("/api/train-station/tickets/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ticket_create_valid(self):
        payload = {
            "cargo": 1,
            "seat": 12,
            "journey": self.journey.id,
            "order": self.order.id

        }
        response = self.client.post("/api/train-station/tickets/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)