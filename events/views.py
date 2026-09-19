# pyrefly: ignore-errors
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Event, Registration
from .permissions import IsOrganizerOrReadOnly, IsOwner
from .serializers import (
    EventDetailSerializer,
    EventListSerializer,
    RegistrationSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    """
    list / retrieve: open to everyone.
    create / update / delete: organizer or staff only.
    Extra action: POST /events/{id}/register/  -> register the current user.
    """

    queryset = Event.objects.select_related("organizer").all()
    permission_classes = [IsOrganizerOrReadOnly]
    filterset_fields = ["organizer"]
    search_fields = ["title", "description", "venue"]
    ordering_fields = ["start_time", "created_at", "title"]

    def get_serializer_class(self):
        if self.action == "list":
            return EventListSerializer
        return EventDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        upcoming = self.request.query_params.get("upcoming")
        if upcoming and upcoming.lower() == "true":
            qs = qs.filter(start_time__gte=timezone.now())
        return qs

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        """Register the current user for this event."""
        event = self.get_object()

        if event.is_past:
            return Response(
                {"detail": "This event has already ended."}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Lock the event row so two simultaneous requests can't both
            # squeeze into the last spot.
            event = Event.objects.select_for_update().get(pk=event.pk)

            existing = Registration.objects.filter(
                user=request.user, event=event, status=Registration.Status.CONFIRMED
            ).first()
            if existing:
                return Response(
                    {"detail": "You are already registered for this event."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if event.is_full:
                return Response(
                    {"detail": "This event is full."}, status=status.HTTP_400_BAD_REQUEST
                )

            try:
                registration = Registration.objects.create(user=request.user, event=event)
            except IntegrityError:
                return Response(
                    {"detail": "You are already registered for this event."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = RegistrationSerializer(registration, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    Users can view and manage only their own registrations.
    DELETE cancels the registration (soft-delete via status) rather than
    removing the row, so organizers keep a record of who dropped out.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = Registration.objects.select_related("user", "event")
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        registration = self.get_object()
        registration.cancel()
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        """Alternative explicit cancel endpoint: PATCH /registrations/{id}/cancel/"""
        registration = self.get_object()
        registration.cancel()
        serializer = self.get_serializer(registration)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email", "")

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from django.contrib.auth import get_user_model
    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response(
        {"detail": "Account created successfully!", "username": user.username},
        status=status.HTTP_201_CREATED,
    )
