from datetime import date, time

from django.core.management.base import BaseCommand
from django.db import transaction

from event.models import Event, FAQ, ScheduleItem, Speaker

DEMO_EVENT_NAME = "Digital Meetup 2026"

DEMO_SPEAKER_NAMES = (
    "Alex Rivera",
    "Jordan Lee",
    "Draft Speaker",
)

DEMO_FAQ_QUESTIONS = (
    "Is the event free to attend?",
    "Will sessions be recorded?",
    "Draft FAQ entry",
)


class Command(BaseCommand):
    help = "Load demo event content (event, speakers, schedule, FAQs) for local review."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove existing demo data before seeding.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace demo data even if it already exists.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"] or options["force"]:
            self._clear_demo_data()

        if Event.objects.filter(name=DEMO_EVENT_NAME).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Demo event '{DEMO_EVENT_NAME}' already exists. "
                    "Use --force to replace it or --clear to remove demo data first."
                )
            )
            return

        event = Event.objects.create(
            name=DEMO_EVENT_NAME,
            description=(
                "Join us for an evening of talks on modern web development, "
                "Django best practices, and building production-ready applications. "
                "Network with peers and learn from industry practitioners."
            ),
            date=date(2026, 9, 15),
            time=time(18, 0),
            location="Kyiv Tech Hub & Online Stream",
        )

        alex = Speaker.objects.create(
            name="Alex Rivera",
            title="Staff Engineer, Cloud Platform",
            description=(
                "Alex builds scalable backend systems and mentors teams on "
                "observability, deployment workflows, and API design."
            ),
            profile_url="https://example.com/speakers/alex-rivera",
            order=1,
            is_published=True,
        )
        jordan = Speaker.objects.create(
            name="Jordan Lee",
            title="Lead Django Developer",
            description=(
                "Jordan focuses on clean domain modeling, admin customization, "
                "and pragmatic testing strategies for Django projects."
            ),
            profile_url="https://example.com/speakers/jordan-lee",
            order=2,
            is_published=True,
        )
        Speaker.objects.create(
            name="Draft Speaker",
            title="To be announced",
            description="This speaker is not published and should not appear on the landing page.",
            order=99,
            is_published=False,
        )

        ScheduleItem.objects.bulk_create(
            [
                ScheduleItem(
                    event=event,
                    start_time=time(18, 0),
                    end_time=time(18, 30),
                    title="Doors open & registration",
                    description="Check in, grab refreshments, and find your seat.",
                ),
                ScheduleItem(
                    event=event,
                    start_time=time(18, 30),
                    end_time=time(19, 15),
                    title="Building reliable Django deployments",
                    description=(
                        "Patterns for settings split, migrations, static files, "
                        "and production hardening on managed platforms."
                    ),
                    speaker=alex,
                ),
                ScheduleItem(
                    event=event,
                    start_time=time(19, 15),
                    end_time=time(20, 0),
                    title="Admin UX that reviewers actually enjoy",
                    description=(
                        "Customizing Django Admin for content editors: filters, "
                        "inlines, CSV export, and validation that catches bad data early."
                    ),
                    speaker=jordan,
                ),
                ScheduleItem(
                    event=event,
                    start_time=time(20, 0),
                    end_time=time(20, 30),
                    title="Networking & wrap-up",
                    description="Open discussion, Q&A, and community announcements.",
                ),
            ]
        )

        FAQ.objects.bulk_create(
            [
                FAQ(
                    question="Is the event free to attend?",
                    answer=(
                        "Yes. Registration is required so we can plan seating and "
                        "send updates before the event."
                    ),
                    order=1,
                    is_published=True,
                ),
                FAQ(
                    question="Will sessions be recorded?",
                    answer=(
                        "Selected talks will be recorded and shared with registered "
                        "participants after the meetup."
                    ),
                    order=2,
                    is_published=True,
                ),
                FAQ(
                    question="Draft FAQ entry",
                    answer="This FAQ is unpublished and should not appear on the public page.",
                    order=99,
                    is_published=False,
                ),
            ]
        )

        self.stdout.write(self.style.SUCCESS(f"Created demo event '{event.name}'."))
        self.stdout.write(
            "Speakers: 2 published, 1 unpublished draft. "
            "FAQs: 2 published, 1 unpublished draft. "
            "Schedule: 4 items."
        )
        self.stdout.write(
            "Images were not uploaded - the landing page uses placeholder graphics "
            "until you add cover/speaker photos in admin."
        )

    def _clear_demo_data(self):
        event_summary = Event.objects.filter(name=DEMO_EVENT_NAME).delete()
        speaker_summary = Speaker.objects.filter(name__in=DEMO_SPEAKER_NAMES).delete()
        faq_summary = FAQ.objects.filter(question__in=DEMO_FAQ_QUESTIONS).delete()

        self.stdout.write(
            "Cleared demo data "
            f"(events cascade: {event_summary[0]} object(s), "
            f"speakers: {speaker_summary[0]}, FAQs: {faq_summary[0]})."
        )
