# pyrefly: ignore-errors
from datetime import timedelta

# pyrefly: ignore-errors
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Event, Registration

User = get_user_model()


class EventRegistrationTests(APITestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="organizer", password="pass12345")
        self.alice = User.objects.create_user(username="alice", password="pass12345")
        self.bob = User.objects.create_user(username="bob", password="pass12345")

        self.event = Event.objects.create(
            title="Tech Fest",
            description="Annual college tech fest",
            venue="Main Auditorium",
            start_time=timezone.now() + timedelta(days=7),
            end_time=timezone.now() + timedelta(days=7, hours=4),
            capacity=1,
            organizer=self.organizer,
        )

    def test_event_list_is_public(self):
        url = reverse("event-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_register_requires_auth(self):
        url = reverse("event-register", kwargs={"pk": self.event.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_and_duplicate_blocked(self):
        self.client.force_authenticate(self.alice)
        url = reverse("event-register", kwargs={"pk": self.event.pk})
        first = self.client.post(url)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(url)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_capacity_enforced(self):
        Registration.objects.create(user=self.alice, event=self.event)  # fills capacity=1

        self.client.force_authenticate(self.bob)
        url = reverse("event-register", kwargs={"pk": self.event.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_cancel_own_registration(self):
        reg = Registration.objects.create(user=self.alice, event=self.event)
        self.client.force_authenticate(self.alice)

        url = reverse("registration-detail", kwargs={"pk": reg.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        reg.refresh_from_db()
        self.assertEqual(reg.status, Registration.Status.CANCELLED)

    def test_user_cannot_cancel_others_registration(self):
        reg = Registration.objects.create(user=self.alice, event=self.event)
        self.client.force_authenticate(self.bob)

        # Bob's queryset is scoped to his own registrations, so someone
        # else's registration doesn't exist as far as he's concerned —
        # a 404 here (rather than 403) also avoids leaking that the
        # object exists at all.
        url = reverse("registration-detail", kwargs={"pk": reg.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_registration_list_scoped_to_user(self):
        Registration.objects.create(user=self.alice, event=self.event)
        another_event = Event.objects.create(
            title="Hack Night",
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=3),
            organizer=self.organizer,
        )
        Registration.objects.create(user=self.bob, event=another_event)

        self.client.force_authenticate(self.alice)
        url = reverse("registration-list")
        response = self.client.get(url)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["user"]["username"], "alice")
