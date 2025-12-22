from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from apps.events.models import Event


User = get_user_model()


@shared_task(name="send_registration_email")
def send_registration_email(user_id: int, event_id: int) -> None:
    try:
        user = User.objects.get(pk=user_id)
        event = Event.objects.select_related("organizer").get(pk=event_id)
    except (User.DoesNotExist, Event.DoesNotExist):
        return
    if not getattr(user, "email", None):
        return
    subject = f"Registration confirmed: {event.title}"
    message = (
        f"Hi {user.get_username()},\n\n"
        f"You are registered for '{event.title}' on {event.date:%Y-%m-%d %H:%M} at {event.location}.\n"
        f"Organizer: {event.organizer.get_username()}\n"
    )
    send_mail(subject, message, getattr(settings, "DEFAULT_FROM_EMAIL", None), [user.email], fail_silently=True)
