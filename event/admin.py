from django.contrib import admin

from .models import Event, FAQ, Registration, ScheduleItem, Speaker


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "location")


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("name",)


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "start_time", "end_time", "speaker")
    list_filter = ("event",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_published")
    list_filter = ("is_published",)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "event", "created_at")
    list_filter = ("event", "created_at")
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
