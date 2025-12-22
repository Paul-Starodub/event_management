from django.urls import include, path
from rest_framework import routers

app_name = "events"

router = routers.DefaultRouter()

urlpatterns = [path("", include(router.urls))]
