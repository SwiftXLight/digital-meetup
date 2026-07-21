from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to="events/covers/", blank=True)

    class Meta:
        ordering = ["-date", "-time"]

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_active(cls):
        return cls.objects.order_by("-date", "-time").first()


class Speaker(models.Model):
    photo = models.ImageField(upload_to="speakers/photos/", blank=True)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField()
    profile_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class ScheduleItem(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="schedule_items",
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    speaker = models.ForeignKey(
        Speaker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedule_items",
    )

    class Meta:
        ordering = ["start_time"]

    def __str__(self) -> str:
        return f"{self.start_time:%H:%M} – {self.title}"

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})


class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self) -> str:
        return self.question


class Registration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    data_consent = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "email"],
                name="unique_registration_per_event",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"
