from django.test import TestCase
from django.urls import reverse

from vng.servervalidation.models import User

from ..models import CustomToken


class TestMultipleEndpoint(TestCase):
    token_manager_url = reverse('apiv1_auth:token-manager')

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('test')
        self.user.save()
        self.client.login(username='test', password='test')

    def test_get_without_existing_token(self):
        response = self.client.get(reverse('apiv1_auth:token-manager'), user=self.user)

        self.assertFalse(response.context_data['tokens'].exists())

    def test_create_token(self):
        response = self.client.post(
            self.token_manager_url,
            {'generate_new': '', 'name': 'newtoken'},
            user=self.user,
            follow=True
        )

        tokens = response.context_data['tokens']
        self.assertEqual(tokens.count(), 1)

        token = tokens.first()
        self.assertIsInstance(token, CustomToken)
        self.assertEqual(token.name, 'newtoken')
        self.assertEqual(token.user, self.user)

    def test_add_second_token(self):
        self.client.post(
            self.token_manager_url,
            {'generate_new': '', 'name': 'token1'},
            user=self.user,
            follow=True
        )

        response = self.client.post(
            self.token_manager_url,
            {'generate_new': '', 'name': 'token2'},
            user=self.user,
            follow=True
        )

        tokens = response.context_data['tokens']
        self.assertEqual(tokens.count(), 2)

        token1 = tokens.first()
        token2 = tokens.last()
        self.assertEqual(token1.name, 'token1')
        self.assertEqual(token2.name, 'token2')

    def test_delete_token(self):
        self.client.post(
            self.token_manager_url,
            {'generate_new': '', 'name': 'token'},
            user=self.user
        )
        response = self.client.post(
            self.token_manager_url,
            {'delete_items': '1'},
            user=self.user,
            follow=True
        )

        self.assertFalse(response.context_data['tokens'].exists())
