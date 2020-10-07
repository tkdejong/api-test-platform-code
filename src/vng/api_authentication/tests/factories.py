import factory
from factory.django import DjangoModelFactory as Dmf

from vng.utils.factories import UserFactory

from ..models import CustomToken


class CustomTokenFactory(Dmf):

    class Meta:
        model = CustomToken

    user = factory.SubFactory(UserFactory)
