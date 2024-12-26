import os
import tempfile
from datetime import timedelta

from PIL import Image
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from train_station.models import Order
from train_station.tests.test_factories import BaseTestCase, sample_route, sample_train, sample_journey, \
    sample_train_type, sample_order

CREW_URL = reverse("train_station:crew-list")


def image_upload_url(crew_id):
    """Return URL for recipe image upload"""
    return reverse("train_station:crew-upload-image", args=[crew_id])


def detail_url(crew_id):
    return reverse("train_station:crew-detail", args=[crew_id])


class CrewImageUploadTests(BaseTestCase):


    def test_upload_image_to_crew(self):
        """Test uploading an image to crew"""
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.crew.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.crew.image.path))


    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.crew.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_upload_image_access_denied(self):
        self.user = get_user_model().objects.create_user(
            email="testimage@test.com",
            password="testpass"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        """Test uploading an invalid image"""
        url = image_upload_url(self.crew.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class RouteViewTests(BaseTestCase):
    def test_filter_by_source_and_destination(self):
        route_test = sample_route(source=self.station1, destination=self.station2)

        res_source = self.client.get(
            reverse("train_station:route-list"), {
                "source": f"{self.station1.id}",
            }
        )

        res_destination = self.client.get(
            reverse("train_station:route-list"), {
                "destination": f"{self.station2.id}",
            }
        )
        self.assertEqual(res_destination.status_code, status.HTTP_200_OK)

        route_source_ids = [route["id"] for route in res_source.data]
        route_destination_ids = [route["id"] for route in res_destination.data]

        self.assertNotIn(self.route.id, route_destination_ids)
        self.assertIn(route_test.id, route_destination_ids)
        self.assertNotIn(self.route.id, route_source_ids)
        self.assertIn(route_test.id, route_source_ids)

    def test_route_list_view(self):
        response = self.client.get(reverse("train_station:route-list"))
        self.assertEqual(response.status_code, 200)
        for route in response.data:
            self.assertIn("source", route)
            self.assertIn("destination", route)
            self.assertNotIn("id", route["source"])
            self.assertNotIn("id", route["destination"])

    def test_route_detail_view(self):
        route_test = sample_route(source=self.station1, destination=self.station2)
        response = self.client.get(reverse("train_station:route-detail", args=[route_test.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data["source"])
        self.assertIn("latitude", response.data["source"])
        self.assertIn("latitude", response.data["destination"])
        self.assertIn("longitude", response.data["source"])


class TrainViewTests(BaseTestCase):
    def test_train_list_view(self):
        response = self.client.get(reverse("train_station:train-list"))
        self.assertEqual(response.status_code, 200)
        for train in response.data:
            self.assertIn("train_type", train)
            self.assertNotIn("id", train["train_type"])

    def test_train_detail_view(self):
        train_test = sample_train()
        response = self.client.get(reverse("train_station:train-detail", args=[train_test.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data["train_type"])


class JourneyViewTests(BaseTestCase):
    def test_filter_by_route(self):
        route = sample_route(
                source=self.station2,
                destination=self.station1
            )
        journey_test = sample_journey(
            train=sample_train(),
            route=route,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=5)
        )

        res = self.client.get(
            reverse("train_station:journey-list"), {
                "route": f"{route.id}",
            }
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        journey_ids = [journey["id"] for journey in res.data]

        self.assertNotIn(self.journey.id, journey_ids)
        self.assertIn(journey_test.id, journey_ids)


    def test_filter_by_depart_and_arrival_time(self):
        journey_test = sample_journey(
            train=sample_train(),
            route=sample_route(),
            departure_time=timezone.now() + timedelta(hours=10),
            arrival_time=timezone.now() + timedelta(hours=15)
        )

        formatted_departure_time = journey_test.departure_time.strftime("%Y-%m-%d %H:%M")
        formatted_arrival_time = journey_test.arrival_time.strftime("%Y-%m-%d %H:%M")

        res_depart = self.client.get(
            reverse("train_station:journey-list"), {
                "departure_time": f"{formatted_departure_time}",
            }
        )

        res_arrive = self.client.get(
            reverse("train_station:journey-list"), {
                "arrival_time": f"{formatted_arrival_time}",
            }
        )
        self.assertEqual(res_depart.status_code, status.HTTP_200_OK)
        self.assertEqual(res_arrive.status_code, status.HTTP_200_OK)

        journey_depart_ids = [journey["id"] for journey in res_depart.data]
        journey_arrive_ids = [journey["id"] for journey in res_arrive.data]

        self.assertNotIn(self.journey.id, journey_depart_ids)
        self.assertIn(journey_test.id, journey_depart_ids)
        self.assertNotIn(self.journey.id, journey_arrive_ids)
        self.assertIn(journey_test.id, journey_arrive_ids)


    def test_journey_list_view(self):
        response = self.client.get(reverse("train_station:journey-list"))
        self.assertEqual(response.status_code, 200)
        for journey in response.data:
            self.assertIn("route_source", journey)
            self.assertIn("route_destination", journey)
            self.assertIn("train", journey)
            self.assertIn("tickets_available", journey)
            self.assertIn("departure_time", journey)
            self.assertIn("arrival_time", journey)

            self.assertNotIn("id", journey["route_source"])
            self.assertNotIn("id", journey["route_destination"])

            self.assertIsInstance(journey["train"], str)

    def test_journey_detail_view(self):
        response = self.client.get(reverse("train_station:journey-detail", args=[self.journey.id]))
        self.assertEqual(response.status_code, 200)

        self.assertIn("id", response.data)
        self.assertIn("route", response.data)
        self.assertIn("train", response.data)
        self.assertIn("crew", response.data)
        self.assertIn("tickets_available", response.data)
        self.assertIn("tickets_available_by_cargo", response.data)
        self.assertIn("departure_time", response.data)
        self.assertIn("arrival_time", response.data)

        self.assertIn("id", response.data["route"])
        self.assertIn("source", response.data["route"])
        self.assertIn("destination", response.data["route"])
        self.assertIn("distance", response.data["route"])

        self.assertIn("id", response.data["train"])
        self.assertIn("name", response.data["train"])
        self.assertIn("train_type", response.data["train"])

        self.assertIsInstance(response.data["crew"], list)

        self.assertIsInstance(response.data["tickets_available_by_cargo"], dict)


class OrderViewTests(BaseTestCase):
    def test_list_orders(self):
        order = sample_order(user=self.user)
        url = reverse("train_station:order-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        order_ids = [order["id"] for order in res.data]
        self.assertIn(order.id, order_ids)

        other_user = get_user_model().objects.create_user("other@myproject.com", "password")
        other_order = sample_order(user=other_user)
        res = self.client.get(url)

        order_ids = [order["id"] for order in res.data]
        self.assertNotIn(other_order.id, order_ids)


    def test_create_order(self):
        url = reverse("train_station:order-list")
        order_data = {
            "tickets": [
                {
                    "journey": str(self.journey.id),
                    "cargo": 1,
                    "seat": 1,
                },
            ]
        }

        res = self.client.post(url, order_data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        created_order = Order.objects.get(id=res.data["id"])
        self.assertEqual(created_order.user, self.user)

        self.assertEqual(created_order.tickets.count(), 1)
        self.assertEqual(created_order.tickets.first().cargo, 1)

    def test_create_order_invalid_ticket(self):
        url = reverse("train_station:order-list")
        order_data = {
            "tickets": [
                {
                    "journey": 999,
                    "cargo": 1,
                    "seat": 1,
                },
            ]
        }

        res = self.client.post(url, order_data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)