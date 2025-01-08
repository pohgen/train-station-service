from rest_framework import routers

from train_station.views import (
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    TrainTypeViewSet,
    JourneyViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()

router.register("crews", CrewViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls

app_name = "train_station"
