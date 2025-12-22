from typing import Optional
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from apps.events.models import Event, EventRegistration
from apps.events.serializers import EventSerializer, EventRegistrationSerializer
from apps.users.serializers import UserShortSerializer
from apps.events.tasks import send_registration_email


User = get_user_model()


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related("organizer")

    def get_serializer_class(self):
        match self.action:
            case "participants":
                return UserShortSerializer
            case "register":
                return EventRegistrationSerializer
            case _:
                return EventSerializer

    def perform_create(self, serializer: EventSerializer) -> None:
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def register(self, request: Request, pk: int | None = None) -> Response:
        event: Event = self.get_object()
        target_user: User = request.user
        participant_id: Optional[int] = request.data.get("participant_id")
        if participant_id is not None:
            if not (request.user.is_staff or request.user.id == event.organizer_id):
                return Response({"detail": "Not allowed to register other users."}, status=status.HTTP_403_FORBIDDEN)
            target_user = get_object_or_404(User, pk=participant_id)
        try:
            registration = EventRegistration.objects.create(event=event, participant=target_user)
        except IntegrityError:
            return Response(
                {"detail": "User is already registered for this event."}, status=status.HTTP_400_BAD_REQUEST
            )
        # send email asynchronously
        transaction.on_commit(lambda: send_registration_email.delay(target_user.id, event.id))
        data = self.get_serializer(registration, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unregister(self, request, pk: int | None = None) -> Response:
        event: Event = self.get_object()
        target_user: User = request.user
        participant_id: Optional[int] = request.query_params.get("participant_id") or request.data.get("participant_id")
        if participant_id is not None:
            if not (request.user.is_staff or request.user.id == event.organizer_id):
                return Response({"detail": "Not allowed to unregister other users."}, status=status.HTTP_403_FORBIDDEN)
            target_user = get_object_or_404(User, pk=participant_id)
        registration = EventRegistration.objects.filter(event=event, participant=target_user).first()
        if not registration:
            return Response({"detail": "Registration not found."}, status=status.HTTP_404_NOT_FOUND)
        registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def participants(self, request: Request, pk: int | None = None) -> Response:
        event: Event = self.get_object()
        users_qs = User.objects.filter(event_registrations__event=event).distinct()
        data = self.get_serializer(users_qs, many=True, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)
