import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Event, FAQ, Registration, ScheduleItem, Speaker


class ScheduleItemInline(admin.TabularInline):
    model = ScheduleItem
    extra = 1
    autocomplete_fields = ("speaker",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "location", "cover_preview")
    readonly_fields = ("cover_preview",)
    inlines = (ScheduleItemInline,)
    fieldsets = (
        (None, {"fields": ("name", "description", "date", "time", "location")}),
        ("Cover image", {"fields": ("cover_image", "cover_preview")}),
    )

    @admin.display(description="Cover preview")
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 120px; border-radius: 4px;" />',
                obj.cover_image.url,
            )
        return "No image uploaded"


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "order", "is_published", "photo_preview")
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("name",)
    readonly_fields = ("photo_preview",)
    fieldsets = (
        (None, {"fields": ("name", "title", "description", "profile_url", "order", "is_published")}),
        ("Photo", {"fields": ("photo", "photo_preview")}),
    )

    @admin.display(description="Photo preview")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 50%;" />',
                obj.photo.url,
            )
        return "No photo uploaded"


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "start_time", "end_time", "speaker")
    list_filter = ("event",)
    search_fields = ("title",)
    autocomplete_fields = ("speaker",)

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_published")
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("question", "answer")


@admin.action(description="Export selected registrations to CSV")
def export_selected_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="registrations.csv"'
    writer = csv.writer(response)
    writer.writerow(["name", "email", "company", "comment", "data_consent", "created_at"])
    for registration in queryset.order_by("created_at"):
        writer.writerow(
            [
                registration.name,
                registration.email,
                registration.company,
                registration.comment,
                registration.data_consent,
                registration.created_at.isoformat(),
            ]
        )
    return response


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "event", "company", "data_consent", "created_at")
    list_filter = ("event", ("created_at", admin.DateFieldListFilter))
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
    actions = (export_selected_to_csv,)
    fieldsets = (
        (None, {"fields": ("event", "name", "email", "company", "comment", "data_consent")}),
        ("System", {"fields": ("created_at",)}),
    )
