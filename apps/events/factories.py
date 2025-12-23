import factory
from django.utils import timezone
from apps.events.models import Event, EventRegistration
from apps.users.factories import UserFactory


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Sequence(lambda n: f"Event #{n}")
    description = factory.Faker("paragraph")
    date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=7))
    location = factory.Faker("city")
    organizer = factory.SubFactory(UserFactory)


class EventRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventRegistration
        django_get_or_create = ("event", "participant")

    event = factory.SubFactory(EventFactory)
    participant = factory.SubFactory(UserFactory)
