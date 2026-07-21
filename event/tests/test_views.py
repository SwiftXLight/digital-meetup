from datetime import date, time

from django.test import Client, TestCase
from django.urls import reverse

from event.models import Event, FAQ, Registration, Speaker


class EventSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.event = Event.objects.create(
            name="Digital Meetup",
            description="Test event description",
            date=date(2026, 8, 1),
            time=time(18, 0),
            location="Online",
        )
        Speaker.objects.create(
            name="Published Speaker",
            title="CEO",
            description="Visible on the landing page.",
            is_published=True,
            order=1,
        )
        Speaker.objects.create(
            name="Hidden Speaker",
            title="CTO",
            description="Should not appear on the landing page.",
            is_published=False,
            order=2,
        )
        FAQ.objects.create(
            question="Published question?",
            answer="Published answer.",
            is_published=True,
            order=1,
        )
        FAQ.objects.create(
            question="Hidden question?",
            answer="Hidden answer.",
            is_published=False,
            order=2,
        )

    def _registration_payload(self, email="user@example.com"):
        return {
            "name": "Jane Doe",
            "email": email,
            "company": "Acme",
            "comment": "Looking forward to it.",
            "data_consent": True,
        }

    def test_home_page_returns_200(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_unpublished_objects_are_hidden_on_home_page(self):
        response = self.client.get("/")

        self.assertContains(response, "Published Speaker")
        self.assertNotContains(response, "Hidden Speaker")
        self.assertContains(response, "Published question?")
        self.assertNotContains(response, "Hidden question?")

    def test_successful_registration_redirects_and_creates_record(self):
        response = self.client.post("/register/", self._registration_payload())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("registration_success"))
        self.assertEqual(Registration.objects.count(), 1)

        registration = Registration.objects.get()
        self.assertEqual(registration.name, "Jane Doe")
        self.assertEqual(registration.email, "user@example.com")
        self.assertEqual(registration.event, self.event)

    def test_duplicate_email_registration_is_blocked(self):
        self.client.post("/register/", self._registration_payload())

        response = self.client.post("/register/", self._registration_payload())

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "A registration with this email already exists for this event.",
        )
        self.assertEqual(Registration.objects.count(), 1)
