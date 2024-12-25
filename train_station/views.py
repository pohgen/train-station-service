from rest_framework import viewsets

from train_station.models import Crew, Station, Route, TrainType, Train, Journey, Order
from train_station.serializers import CrewSerializer, StationSerializer, OrderSerializer, \
    JourneySerializer, TrainSerializer, TrainTypeSerializer, RouteSerializer, RouteListSerializer, \
    RouteDetailSerializer, TrainListSerializer, TrainDetailSerializer, JourneyDetailSerializer, JourneyListSerializer, \
    OrderListSerializer


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
            destination_ids = self._params_to_ints(destination)
            queryset = queryset.filter(destination__id__in=destination_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        route = self.request.query_params.get("route")
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")


        queryset = self.queryset

        if route:
            route_ids = self._params_to_ints(route)
            queryset = queryset.filter(route__id__in=route_ids)

        if departure_time:
            queryset = queryset.filter(departure_time__startswith=departure_time)

        if arrival_time:
            queryset = queryset.filter(arrival_time__startswith=arrival_time)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route",
        "tickets__journey__train",
        "tickets__journey__crew"
    )
    serializer_class = OrderSerializer

    # def get_queryset(self):
    #     return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderListSerializer

        return OrderSerializer

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
