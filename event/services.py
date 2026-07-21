from .models import Event, Registration


def register_participant(event: Event, cleaned_data: dict) -> Registration:
    return Registration.objects.create(event=event, **cleaned_data)
