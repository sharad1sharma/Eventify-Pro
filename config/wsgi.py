import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()


def _ensure_db_initialized():
    try:
        from django.db import connection

        tables = connection.introspection.table_names()
        if "events_event" not in tables:
            from django.core.management import call_command

            call_command("migrate", interactive=False)

            from datetime import timedelta
            from django.contrib.auth import get_user_model
            from django.utils import timezone
            from events.models import Event

            User = get_user_model()
            admin_user, created = User.objects.get_or_create(
                username="admin",
                defaults={
                    "email": "admin@eventify.pro",
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            if created or not admin_user.has_usable_password():
                admin_user.set_password("admin123")
                admin_user.save()

            demo_user, d_created = User.objects.get_or_create(
                username="demouser",
                defaults={"email": "demo@eventify.pro"},
            )
            if d_created or not demo_user.has_usable_password():
                demo_user.set_password("demo123")
                demo_user.save()

            if Event.objects.count() == 0:
                now = timezone.now()
                Event.objects.create(
                    title="AI & Web Tech Summit 2026",
                    description="Explore cutting-edge breakthroughs in Generative AI, cloud deployments, and modern web architectures.",
                    venue="Innovation Hall & Virtual Stream",
                    start_time=now + timedelta(days=7),
                    end_time=now + timedelta(days=7, hours=4),
                    capacity=150,
                    organizer=admin_user,
                )
                Event.objects.create(
                    title="Django REST Framework Masterclass",
                    description="Hands-on deep dive into scalable REST APIs, token authentication, and database query optimization.",
                    venue="Tech Hub Room 402",
                    start_time=now + timedelta(days=14),
                    end_time=now + timedelta(days=14, hours=3),
                    capacity=60,
                    organizer=admin_user,
                )
                Event.objects.create(
                    title="Global Open Source Hackathon",
                    description="Collaborate with developers worldwide to build impactful open-source tools and community applications.",
                    venue="Global Discord & Main Stage",
                    start_time=now + timedelta(days=21),
                    end_time=now + timedelta(days=23),
                    capacity=500,
                    organizer=admin_user,
                )
    except Exception as err:
        print("Vercel DB initialization notice:", err)


_ensure_db_initialized()

app = application
