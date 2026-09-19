# pyrefly: ignore-errors
from django.conf import settings
from django.db import models
from django.utils import timezone


class Event(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    venue = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(
        default=0, help_text="Maximum number of confirmed registrations. 0 = unlimited."
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return str(self.title)

    @property
    def is_past(self):
        return self.end_time < timezone.now()

    @property
    def confirmed_count(self):
        return self.registrations.filter(status=Registration.Status.CONFIRMED).count()

    @property
    def spots_left(self):
        if self.capacity == 0:
            return None  # unlimited
        return max(self.capacity - self.confirmed_count, 0)

    @property
    def is_full(self):
        return self.capacity != 0 and self.spots_left == 0


class Registration(models.Model):
    objects = models.Manager()
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-registered_at"]
        constraints = [
            # A user can only have ONE active (confirmed) registration per event.
            # They can re-register after cancelling, which creates a new row.
            models.UniqueConstraint(
                fields=["user", "event"],
                condition=models.Q(status="confirmed"),
                name="unique_active_registration_per_user_event",
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"

    def cancel(self):
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancelled_at"])
