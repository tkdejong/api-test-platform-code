from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from vng.servervalidation.models import User
from vng.testsession.tests.factories import UserFactory


class TestMultipleEndpoint(TestCase):
    token_manager_url = reverse('apiv1_auth:token-manager')

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('test')
        self.user.save()
        self.client.login(username='test', password='test')

    def test_get_without_existing_token(self):
        response = self.client.get(reverse('apiv1_auth:token-manager'), user=self.user)

        self.assertIsNone(response.context_data['token'])

    def test_create_token(self):
        response = self.client.post(
            self.token_manager_url,
            {'generate_new': ''},
            user=self.user,
            follow=True
        )

        token = response.context_data['token']
        self.assertIsInstance(token, Token)
        self.assertEqual(token.user, self.user)

    def test_generate_new_token(self):
        response = self.client.post(
            self.token_manager_url,
            {'generate_new': ''},
            user=self.user,
            follow=True
        )
        old_token = response.context_data['token']

        response = self.client.post(
            self.token_manager_url,
            {'generate_new': ''},
            user=self.user,
            follow=True
        )
        new_token = response.context_data['token']
        self.assertIsInstance(new_token, Token)
        self.assertEqual(new_token.user, self.user)

        self.assertNotEqual(old_token, new_token)

    def test_delete_token(self):
        self.client.post(
            self.token_manager_url,
            {'generate_new': ''},
            user=self.user
        )
        response = self.client.post(
            self.token_manager_url,
            {'delete': ''},
            user=self.user,
            follow=True
        )

        self.assertIsNone(response.context_data['token'])
