from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters
from apps.events.models import Event


class EventFilter(filters.FilterSet):
    organizer = filters.NumberFilter(field_name="organizer_id")
    search = filters.CharFilter(method="filter_search", label="Search")

    class Meta:
        model = Event
        fields = ["organizer", "search"]

    def filter_search(self, qs, name, value) -> QuerySet:
        if not value:
            return qs
        terms = [term for term in value.split() if term]
        for term in terms:
            qs = qs.filter(
                Q(title__icontains=term)
                | Q(description__icontains=term)
                | Q(location__icontains=term)
                | Q(organizer__username__icontains=term)
                | Q(organizer__first_name__icontains=term)
                | Q(organizer__last_name__icontains=term)
            )
        return qs
