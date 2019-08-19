from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from vng.servervalidation.models import User

from .factories import CustomTokenFactory
from ..models import CustomToken


class TestMultipleEndpoint(TestCase):
    token_manager_url = reverse('apiv1_auth:token-manager')
    login_url = reverse('apiv1_auth:rest_login')
    logout_url = reverse('apiv1_auth:rest_logout')
    session_types_url = reverse('apiv1session:session_types-list')

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

    def test_login_with_multiple_tokens(self):
        CustomTokenFactory.create(name='token1', user=self.user)
        token2 = CustomTokenFactory.create(name='token2', user=self.user)

        response = self.client.post(
            self.login_url, {'username': self.user.username, 'password': 'test'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['key'], token2.key)

    def test_logout_with_multiple_tokens(self):
        CustomTokenFactory.create(name='token1', user=self.user)
        CustomTokenFactory.create(name='token2', user=self.user)

        self.client.post(
            self.login_url, {'username': self.user.username, 'password': 'test'}
        )

        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticate_with_multiple_tokens(self):
        token1 = CustomTokenFactory.create(name='token1', user=self.user)
        token2 = CustomTokenFactory.create(name='token2', user=self.user)

        response1 = self.client.get(
            self.session_types_url,
            HTTP_AUTHORIZATION='Token {}'.format(token1.key)
        )

        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.get(
            self.session_types_url,
            HTTP_AUTHORIZATION='Token {}'.format(token2.key)
        )

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response2.data)

    def test_unauthorized(self):
        self.client.post(self.logout_url)
        response1 = self.client.get(self.session_types_url)
        self.assertEqual(response1.status_code, status.HTTP_401_UNAUTHORIZED)
