from rest_framework import serializers
from apps.events.models import Event
from apps.users.models import User
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


class BulkParticipantsSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, required=True, write_only=True
    )

    def validate(self, attrs: dict) -> dict:
        ids_set = set(attrs["participant_ids"])
        existing_ids = set(User.objects.filter(id__in=ids_set).values_list("id", flat=True))
        if len(existing_ids) != len(ids_set):
            missing = sorted(ids_set - existing_ids)
            raise serializers.ValidationError({"participant_ids": f"Users not found: {missing}"})
        return attrs
