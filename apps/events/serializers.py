from rest_framework import serializers
from apps.events.models import Event, EventRegistration
from apps.users.serializers import UserShortSerializer


class EventSerializer(serializers.ModelSerializer):
    organizer = UserShortSerializer(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "location",
            "organizer",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "organizer", "created_at", "updated_at")


class EventRegistrationSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(read_only=True)
    participant = UserShortSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = ("id", "event", "participant", "registered_at")
        read_only_fields = ("id", "event", "participant", "registered_at")
