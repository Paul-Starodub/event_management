import factory
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    is_staff = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or get_random_string(12)
        self.set_password(raw_password)
        self._raw_password = raw_password
