from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "date", "location", "organizer", "created_at")
    list_filter = ("date", "location", "organizer")
    search_fields = ("title", "description", "location", "organizer__username")


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "participant", "registered_at")
    list_filter = ("registered_at", "event")
    search_fields = ("event__title", "participant__username", "participant__email")
