from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from apps.events.filters import EventFilter
from apps.events.models import Event, EventRegistration
from apps.events.serializers import EventSerializer, BulkParticipantsSerializer
from apps.users.serializers import UserShortSerializer
from apps.events.tasks import send_registration_email


User = get_user_model()


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related("organizer")
    filterset_class = EventFilter

    def get_serializer_class(self):
        match self.action:
            case "participants":
                return UserShortSerializer
            case "register" | "unregister":
                return BulkParticipantsSerializer
            case _:
                return EventSerializer

    def perform_create(self, serializer: EventSerializer) -> None:
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def register(self, request: Request, pk: int | None = None) -> Response:
        event: Event = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant_ids: list[int] = serializer.validated_data["participant_ids"]
        already_registered_ids: set[int] = set(
            EventRegistration.objects.filter(event=event, participant_id__in=participant_ids).values_list(
                "participant_id", flat=True
            )
        )
        to_create_ids: list[int] = [uid for uid in participant_ids if uid not in already_registered_ids]
        if to_create_ids:
            EventRegistration.objects.bulk_create(
                [EventRegistration(event=event, participant_id=uid) for uid in to_create_ids], ignore_conflicts=True
            )
            transaction.on_commit(lambda: [send_registration_email.delay(uid, event.id) for uid in to_create_ids])
        return Response(
            {
                "event_id": event.id,
                "created_ids": to_create_ids,
                "already_registered_ids": sorted(already_registered_ids),
                "created_count": len(to_create_ids),
            },
            status=status.HTTP_201_CREATED if to_create_ids else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unregister(self, request: Request, pk: int | None = None) -> Response:
        event: Event = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant_ids: list[int] = serializer.validated_data["participant_ids"]
        qs = EventRegistration.objects.filter(event=event, participant_id__in=participant_ids)
        existing_ids: set[int] = set(qs.values_list("participant_id", flat=True))
        deleted_count, _ = qs.delete()
        not_found_ids = sorted(set(participant_ids) - existing_ids)
        return Response(
            {
                "event_id": event.id,
                "deleted_ids": sorted(existing_ids),
                "not_found_ids": not_found_ids,
                "deleted_count": deleted_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def participants(self, request: Request, pk: int | None = None) -> Response:
        event: Event = self.get_object()
        users_qs = User.objects.filter(event_registrations__event=event).distinct()
        page = self.paginate_queryset(users_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(users_qs, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
