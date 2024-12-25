from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from train_station.models import TrainType, Train, Crew, Station, Route, Journey, Order, Ticket
from train_station.serializers import RouteSerializer
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
        self.station2 = Station.objects.create(name="Kharkiv")
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

    def test_filter_routes_by_source(self):
        station_test = Station.objects.create(name="Oslo")
        route_test = Route.objects.create(source=station_test, destination=self.station1)

        res = self.client.get(
            reverse("train_station:route-list"), {
                "source": f"{station_test.id}",
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        route_ids = [route["id"] for route in res.data]

        self.assertNotIn(self.route.id, route_ids)
        self.assertIn(route_test.id, route_ids)

    def test_filter_routes_by_destination(self):
        station_test = Station.objects.create(name="Oslo")
        route_test = Route.objects.create(source=self.station1, destination=station_test)

        res = self.client.get(
            reverse("train_station:route-list"), {
                "destination": f"{station_test.id}",
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        route_ids = [route["id"] for route in res.data]

        self.assertNotIn(self.route.id, route_ids)
        self.assertIn(route_test.id, route_ids)

    def test_filter_journey_by_route(self):
        station_test = Station.objects.create(name="Oslo")
        route_test = Route.objects.create(source=self.station1, destination=station_test)
        journey_test = Journey.objects.create(
            route=route_test,
            train=self.train,
            departure_time=timezone.now() + timedelta(hours=2),
            arrival_time=timezone.now() + timedelta(hours=5)
        )
        journey_test.crew.add(self.crew,)

        res = self.client.get(
            reverse("train_station:journey-list"), {
                "route": f"{route_test.id}",
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        journey_ids = [journey["id"] for journey in res.data]

        self.assertNotIn(self.journey.id, journey_ids)
        self.assertIn(journey_test.id, journey_ids)

    def test_filter_journey_by_departure_time(self):
        station_test = Station.objects.create(name="Oslo")
        route_test = Route.objects.create(source=self.station1, destination=station_test)
        journey_test = Journey.objects.create(
            route=route_test,
            train=self.train,
            departure_time=timezone.now() + timedelta(hours=10),
            arrival_time=timezone.now() + timedelta(hours=12)
        )
        journey_test.crew.add(self.crew,)

        formatted_departure_time = journey_test.departure_time.strftime("%Y-%m-%d %H:%M")

        res = self.client.get(
            reverse("train_station:journey-list"), {
                "departure_time": f"{formatted_departure_time}",
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        journey_ids = [journey["id"] for journey in res.data]

        self.assertNotIn(self.journey.id, journey_ids)
        self.assertIn(journey_test.id, journey_ids)

    def test_filter_journey_by_arrival_time(self):
        station_test = Station.objects.create(name="Oslo")
        route_test = Route.objects.create(source=self.station1, destination=station_test)
        journey_test = Journey.objects.create(
            route=route_test,
            train=self.train,
            departure_time=timezone.now() + timedelta(hours=10),
            arrival_time=timezone.now() + timedelta(hours=12)
        )
        journey_test.crew.add(self.crew,)

        formatted_arrival_time = journey_test.arrival_time.strftime("%Y-%m-%d %H:%M")

        res = self.client.get(
            reverse("train_station:journey-list"), {
                "arrival_time": f"{formatted_arrival_time}",
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        journey_ids = [journey["id"] for journey in res.data]

        self.assertNotIn(self.journey.id, journey_ids)
        self.assertIn(journey_test.id, journey_ids)