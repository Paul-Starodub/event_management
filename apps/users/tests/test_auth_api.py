from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.users.factories import UserFactory


User = get_user_model()


class AuthApiTests(APITestCase):
    def test_register_user(self) -> None:
        url = reverse("users:create")
        payload = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "strongpassword",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertEqual(res.data["username"], payload["username"])
        self.assertEqual(res.data["email"], payload["email"])
        self.assertNotIn("password", res.data)
        self.assertTrue(User.objects.filter(username="new_user").exists())

    def test_login_and_me(self) -> None:
        user = UserFactory()
        assert hasattr(user, "_raw_password")
        login_url = reverse("users:login")
        res = self.client.post(
            login_url,
            {"username": user.username, "password": user._raw_password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

        access = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        me_url = reverse("users:manage")
        me = self.client.get(me_url)
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], user.username)

    def test_user_viewset_list_is_public(self) -> None:
        UserFactory.create_batch(3)
        url = reverse("users:all-users-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 3)
