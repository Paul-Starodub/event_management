from rest_framework import routers
from apps.events.views import EventViewSet

app_name = "events"

router = routers.DefaultRouter()
router.register("", EventViewSet, basename="events")

urlpatterns = router.urls
