from django.shortcuts import render
from django.template.defaultfilters import title
from rest_framework import viewsets

from train_station.models import Crew, Station, Route, TrainType, Train, Journey, Order, Ticket
from train_station.serializers import CrewSerializer, StationSerializer, TicketSerializer, OrderSerializer, \
    JourneySerializer, TrainSerializer, TrainTypeSerializer, RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination =self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            source_ids = self._params_to_ints(source)
            queryset = queryset.filter(source__id__in=source_ids)

        if destination:
            destination_ids = self._params_to_ints(source)
            queryset = queryset.filter(destination__id__in=destination_ids)

        return queryset.distinct()


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer