from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from train_station.models import (
    Crew,
    Station,
    Route,
    TrainType,
    Train,
    Journey,
    Order,
    Ticket,
)


def sample_crew(**params):
    defaults = {
        "first_name": "Nikita",
        "last_name": "Tkachenko",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": "Oslo",
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_station(name="Kyiv"),
        "destination": sample_station(name="Lviv"),
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_train_type(**params):
    defaults = {"name": "Passenger"}
    defaults.update(params)
    return TrainType.objects.create(**defaults)


def sample_train(**params):
    defaults = {
        "name": "Express-1",
        "cargo_num": 5,
        "places_in_cargo": 50,
        "train_type": sample_train_type(),
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_journey(**params):
    defaults = {
        "route": sample_route(),
        "train": sample_train(),
        "departure_time": timezone.now(),
        "arrival_time": timezone.now() + timedelta(hours=5),
    }
    defaults.update(params)
    journey = Journey.objects.create(**defaults)
    journey.crew.add(sample_crew())
    return journey


def sample_order(**params):
    user, _ = get_user_model().objects.get_or_create(
        email="testuser@test.com",
        defaults={"password": "testpass", "is_superuser": True, "is_staff": True},
    )
    defaults = {"user": user}
    defaults.update(params)
    return Order.objects.create(**defaults)


def sample_ticket(**params):
    defaults = {
        "cargo": 1,
        "seat": 10,
        "journey": sample_journey(),
        "order": sample_order(),
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


class BaseTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="testuser@test.com", password="testpass"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.station = sample_station()
        self.station1 = sample_station(name="Kharkiv")
        self.station2 = sample_station(name="Paris")
        self.route = sample_route()
        self.train_type = sample_train_type()
        self.train = sample_train()
        self.crew = sample_crew()
        self.journey = sample_journey()
        self.order = sample_order()
        self.ticket = sample_ticket()

    def tearDown(self):
        get_user_model().objects.all().delete()
        self.crew.image.delete()
