from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Event, Registration

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the event list endpoint."""

    organizer = UserBriefSerializer(read_only=True)
    spots_left = serializers.SerializerMethodField()
    is_full = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    confirmed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "venue",
            "start_time",
            "end_time",
            "capacity",
            "spots_left",
            "confirmed_count",
            "is_full",
            "is_past",
            "organizer",
        ]

    def get_spots_left(self, obj):
        return obj.spots_left


class EventDetailSerializer(serializers.ModelSerializer):
    """Full serializer for event detail / create / update."""

    organizer = UserBriefSerializer(read_only=True)
    spots_left = serializers.SerializerMethodField()
    is_full = serializers.BooleanField(read_only=True)
    confirmed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "venue",
            "start_time",
            "end_time",
            "capacity",
            "spots_left",
            "is_full",
            "confirmed_count",
            "organizer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["organizer", "created_at", "updated_at"]

    def get_spots_left(self, obj):
        return obj.spots_left

    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError("end_time must be after start_time.")
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    event_detail = EventListSerializer(source="event", read_only=True)

    class Meta:
        model = Registration
        fields = [
            "id",
            "user",
            "event",
            "event_detail",
            "status",
            "registered_at",
            "cancelled_at",
        ]
        read_only_fields = ["user", "status", "registered_at", "cancelled_at"]
        extra_kwargs = {"event": {"write_only": True}}

    def validate_event(self, event):
        if event.is_past:
            raise serializers.ValidationError("You can't register for an event that has already ended.")
        return event
