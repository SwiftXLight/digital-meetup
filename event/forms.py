from django import forms
from django.core.exceptions import ValidationError

from .models import Registration


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ["name", "email", "company", "comment", "data_consent"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "company": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 3},
            ),
            "data_consent": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "data_consent": "I agree to the processing of my personal data",
        }

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        self.fields["data_consent"].required = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        if (
            self.event
            and Registration.objects.filter(
                event=self.event,
                email__iexact=email,
            ).exists()
        ):
            raise ValidationError(
                "A registration with this email already exists for this event."
            )
        return email

    def clean_data_consent(self):
        data_consent = self.cleaned_data.get("data_consent")
        if not data_consent:
            raise ValidationError("You must agree to the processing of your personal data.")
        return data_consent

    def save(self, commit=True):
        registration = super().save(commit=False)
        registration.event = self.event
        if commit:
            registration.save()
        return registration
