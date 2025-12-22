from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name="Event Title")
    description = models.TextField(blank=True, verbose_name="Event Description")
    date = models.DateTimeField(verbose_name="Event Date and Time")
    location = models.CharField(max_length=255, verbose_name="Event Location")
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organized_events", verbose_name="Organizer"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Event Creation Date and Time")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Event Last Update Date and Time")

    class Meta:
        ordering = ("date", "title")

    def __str__(self) -> str:
        return f"{self.title} @ {self.location} on {self.date:%Y-%m-%d %H:%M}"


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations", verbose_name="Event")
    participant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_registrations", verbose_name="User"
    )
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="Registration Date and Time")

    class Meta:
        unique_together = ("event", "participant")
        ordering = ["-registered_at"]

    def __str__(self) -> str:
        return f"{self.participant} -> {self.event}"
