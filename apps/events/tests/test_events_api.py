from datetime import timedelta
from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from apps.events.factories import EventFactory
from apps.events.models import Event, EventRegistration
from apps.users.factories import UserFactory


class EventApiTests(APITestCase):
    def authenticate(self, user=None) -> None:
        if user is None:
            user = UserFactory()
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")
        self._auth_user = user

    def test_list_requires_authentication(self) -> None:
        url = reverse("events:events-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated(self) -> None:
        self.authenticate()
        EventFactory.create_batch(3)
        url = reverse("events:events-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("results", res.data)
        self.assertGreaterEqual(len(res.data["results"]), 1)

    def test_create_event_sets_organizer(self) -> None:
        self.authenticate()
        url = reverse("events:events-list")
        payload = {
            "title": "Conf 2025",
            "description": "Annual conf",
            "date": (timezone.now() + timedelta(days=10)).isoformat(),
            "location": "NYC",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(id=res.data["id"])
        self.assertEqual(event.organizer_id, self._auth_user.id)

    @patch("apps.events.views.send_registration_email")
    def test_register_and_unregister_participants(self, mock_task) -> None:
        mock_task.delay.return_value = None
        self.authenticate()
        event = EventFactory(organizer=self._auth_user)
        users = UserFactory.create_batch(3)
        register_url = reverse("events:events-register", args=[event.id])
        payload = {"participant_ids": [users[0].id, users[1].id]}
        res = self.client.post(register_url, payload, format="json")
        self.assertIn(res.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        self.assertEqual(sorted(res.data["created_ids"]), sorted(payload["participant_ids"]))
        self.assertEqual(res.data["created_count"], 2)
        self.assertEqual(EventRegistration.objects.filter(event=event).count(), 2)
        res2 = self.client.post(register_url, payload, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["created_ids"], [])
        self.assertEqual(sorted(res2.data["already_registered_ids"]), sorted(payload["participant_ids"]))
        unregister_url = reverse("events:events-unregister", args=[event.id])
        res3 = self.client.post(unregister_url, {"participant_ids": [users[0].id]}, format="json")
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertEqual(res3.data["deleted_count"], 1)
        self.assertEqual(EventRegistration.objects.filter(event=event).count(), 1)
        participants_url = reverse("events:events-participants", args=[event.id])
        res4 = self.client.get(participants_url)
        self.assertEqual(res4.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(res4.data, list) or "results" in res4.data)
