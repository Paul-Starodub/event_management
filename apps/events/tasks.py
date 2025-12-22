from celery import shared_task
from apps.events.services.registration_email import send_registration_confirmation_email


@shared_task(name="send_registration_email")
def send_registration_email(user_id: int, event_id: int) -> None:
    send_registration_confirmation_email(user_id, event_id)
