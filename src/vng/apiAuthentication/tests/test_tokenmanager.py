from django.contrib.auth import get_user_model
from django.urls import reverse

import factory
from django_webtest import WebTest

from vng.servervalidation.models import (
    PostmanTest, PostmanTestResult, ServerRun, User
)
from vng.testsession.tests.factories import UserFactory

from .factories import TokenFactory


class TestMultipleEndpoint(WebTest):

    def setUp(self):
        self.user = UserFactory.create()

    def test_generate_new_token(self):
        self.client.get(reverse('apiv1_auth:token-manager'), user=self.user)
