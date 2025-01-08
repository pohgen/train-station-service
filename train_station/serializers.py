from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count
from rest_framework import serializers

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


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "image")


class CrewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("image",)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")
        read_only_fields = ("latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")
        read_only_fields = ("distance",)


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    train_type = serializers.CharField(source="train_type.name", read_only=True)


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(read_only=True)


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "crew", "departure_time", "arrival_time")


class JourneyListSerializer(JourneySerializer):
    route_source = serializers.CharField(source="route.source.name", read_only=True)
    route_destination = serializers.CharField(
        source="route.destination.name", read_only=True
    )
    train = serializers.CharField(source="train.name", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route_source",
            "route_destination",
            "train",
            "tickets_available",
            "departure_time",
            "arrival_time",
        )


class JourneyDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(read_only=True)
    train = TrainDetailSerializer(read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    tickets_available = serializers.IntegerField(read_only=True)
    tickets_available_by_cargo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "tickets_available",
            "tickets_available_by_cargo",
            "departure_time",
            "arrival_time",
        )

    def to_representation(self, instance):
        queryset = Crew.objects.prefetch_related("full_name")
        return super().to_representation(instance)

    def get_tickets_available_by_cargo(self, obj):
        max_seats = obj.train.places_in_cargo
        cargos = obj.train.cargo_num

        tickets_count_by_cargo = (
            obj.tickets.values("cargo")
            .annotate(ticket_count=Count("cargo"))
            .values("cargo", "ticket_count")
        )

        free_seats = {i: max_seats for i in range(1, cargos + 1)}

        for ticket in tickets_count_by_cargo:
            free_seats[ticket["cargo"]] -= ticket["ticket_count"]

        return free_seats


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"], attrs["seat"], attrs["journey"].train, ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
