from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import RegistrationForm
from .models import Event, FAQ, Speaker
from .services import register_participant


def _landing_context(event, form):
    return {
        "event": event,
        "speakers": Speaker.objects.filter(is_published=True),
        "schedule_items": (
            event.schedule_items.select_related("speaker") if event else []
        ),
        "faqs": FAQ.objects.filter(is_published=True),
        "form": form,
    }


def landing(request):
    event = Event.get_active()
    form = RegistrationForm(event=event)
    return render(request, "event/index.html", _landing_context(event, form))


@require_POST
def register(request):
    event = Event.get_active()
    if not event:
        return redirect("landing")

    form = RegistrationForm(request.POST, event=event)
    if form.is_valid():
        try:
            register_participant(event, form.cleaned_data)
        except IntegrityError:
            form.add_error("email", RegistrationForm.DUPLICATE_EMAIL_MESSAGE)
        else:
            return redirect("registration_success")

    return render(
        request,
        "event/index.html",
        _landing_context(event, form),
    )


def registration_success(request):
    return render(request, "event/registration_success.html")
