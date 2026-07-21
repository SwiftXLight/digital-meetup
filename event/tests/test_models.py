from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase

from event.models import Event, ScheduleItem


class ScheduleItemValidationTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="Digital Meetup",
            description="Test event",
            date=date(2026, 8, 1),
            time=time(18, 0),
            location="Online",
        )

    def test_end_time_must_be_after_start_time(self):
        item = ScheduleItem(
            event=self.event,
            start_time=time(10, 0),
            end_time=time(9, 0),
            title="Invalid talk",
            description="Should fail validation.",
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_equal_start_and_end_time_is_invalid(self):
        item = ScheduleItem(
            event=self.event,
            start_time=time(10, 0),
            end_time=time(10, 0),
            title="Invalid talk",
            description="Should fail validation.",
        )

        with self.assertRaises(ValidationError):
            item.full_clean()
