from django.utils import timezone
import factory
from factory.django import DjangoModelFactory as Dmf
from vng.accounts.models import User
from ..models import SessionType, Session


class SessionTypeFactory(Dmf):

    class Meta:
        model = SessionType

    name = factory.sequence(lambda n:'testype %d' % n)
    docker_image = 'di'


class SessionFactory(Dmf):

    class Meta:
        model = Session

    session_type = 1
    started = timezone.now()
    status = Session.StatusChoices.starting
    user = 1
    api_endpoint = 'http://google.com'

class UserFactory(Dmf):

    class Meta:
        model = User

    username = 'test'
    password = factory.PostGenerationMethodCall('set_password', 'pippopippo')