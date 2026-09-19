# pyrefly: ignore-errors
from django.contrib import admin

from .models import Event, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ("user", "status", "registered_at", "cancelled_at")
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_time", "end_time", "venue", "organizer", "capacity_display")
    list_filter = ("start_time",)
    search_fields = ("title", "description", "venue")
    date_hierarchy = "start_time"
    inlines = (RegistrationInline,)

    @admin.display(description="Capacity")
    def capacity_display(self, obj):
        if obj.capacity == 0:
            return f"{obj.confirmed_count} (unlimited)"
        return f"{obj.confirmed_count}/{obj.capacity}"

    def save_model(self, request, obj, form, change):
        if not obj.organizer_id:
            obj.organizer = request.user
        super().save_model(request, obj, form, change)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "registered_at", "cancelled_at")
    list_filter = ("status", "event")
    search_fields = ("user__username", "user__email", "event__title")
    actions = ("cancel_registrations",)

    @admin.action(description="Cancel selected registrations")
    def cancel_registrations(self, request, queryset):
        for reg in queryset.filter(status=Registration.Status.CONFIRMED):
            reg.cancel()
