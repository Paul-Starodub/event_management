from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User
from apps.events.models import Event


class Command(BaseCommand):
    help = "Create 3 users and 5 events (no registrations)"

    def handle(self, *args, **options) -> None:
        self.stdout.write("Creating 3 users...")
        usernames = ["user1", "user2", "user3"]
        users: list[User] = []
        for uname in usernames:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    "email": f"{uname}@example.com",
                },
            )
            if created:
                user.set_password("password123")
                if uname == "user1":
                    user.is_staff = True
                    user.is_superuser = True
                user.save(update_fields=["password", "is_staff", "is_superuser"])
            else:
                if uname == "user1" and (not user.is_superuser or not user.is_staff):
                    user.is_staff = True
                    user.is_superuser = True
                    user.save(update_fields=["is_staff", "is_superuser"])
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"Users ready: {[u.username for u in users]}"))

        self.stdout.write("Creating 5 events (real objects)...")
        events: list[Event] = []
        titles = [f"Event {i}" for i in range(1, 6)]
        now = timezone.now()
        for i, title in enumerate(titles, start=1):
            organizer = users[(i - 1) % len(users)]
            event, _ = Event.objects.get_or_create(
                title=title,
                date=now + timezone.timedelta(days=i),
                defaults={
                    "description": f"Description for {title}",
                    "location": f"City {i}",
                    "organizer": organizer,
                },
            )
            events.append(event)
        self.stdout.write(self.style.SUCCESS(f"Events ready: {[e.title for e in events]}"))
        self.stdout.write(self.style.SUCCESS("Done."))
