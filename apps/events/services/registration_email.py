from __future__ import annotations
from dataclasses import dataclass
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from apps.events.models import Event


User = get_user_model()


@dataclass(frozen=True)
class RegistrationEmail:
    subject: str
    message: str
    from_email: str | None
    to_email: str


def build_registration_email(user: User, event: Event) -> RegistrationEmail:
    if not getattr(user, "email", None):
        raise ValueError("User has no email")
    event_dt = timezone.localtime(event.date) if timezone.is_aware(event.date) else event.date
    subject = f"Registration confirmed: {event.title}"
    message = (
        f"Hi {user.get_username()},\n\n"
        f"You are registered for '{event.title}' on {event_dt:%Y-%m-%d %H:%M} at {event.location}.\n"
        f"Organizer: {event.organizer.get_username()}\n"
    )
    return RegistrationEmail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to_email=user.email,
    )


def send_registration_confirmation_email(user_id: int, event_id: int, *, fail_silently: bool = True) -> bool:
    try:
        user = User.objects.get(pk=user_id)
        event = Event.objects.select_related("organizer").get(pk=event_id)
    except (User.DoesNotExist, Event.DoesNotExist):
        return False
    if not getattr(user, "email", None):
        return False
    email = build_registration_email(user, event)
    sent_email = send_mail(
        email.subject,
        email.message,
        email.from_email,
        [email.to_email],
        fail_silently=fail_silently,
    )
    return bool(sent_email)
