import collections
import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from django_webtest import TransactionWebTest, WebTest
from django.urls import reverse

from rest_framework import status
from vng.accounts.models import User

from ..models import PostmanTestResult
from .factories import ServerRunFactory, TestScenarioFactory, TestScenarioUrlFactory, PostmanTestFactory, PostmanTestNoAssertionFactory, EndpointFactory
from ...utils.factories import UserFactory


def get_object(r):
    return json.loads(r.decode('utf-8'))


def get_username():
    l = User.objects.all()
    if len(l) != 0:
        return l.first().username
    return UserFactory().username


def create_server_run(name, tsu):
    endpoints = []
    for t in tsu:
        endpoints.append({
            "test_scenario_url": {
                "name": t.name
            },
            'url': 'https://google.com',
        })
    return {
        'test_scenario': name,
        'client_id': 'client_id_field',
        'secret': 'secret_field',
        'endpoints': endpoints
    }


class RetrieveCreationTest(TransactionWebTest):

    def setUp(self):
        self.test_scenario = PostmanTestFactory().test_scenario
        tsu1 = TestScenarioUrlFactory()
        tsu2 = TestScenarioUrlFactory()
        tsu1.test_scenario = self.test_scenario
        tsu2.test_scenario = self.test_scenario
        tsu1.save()
        tsu2.save()
        self.server_run = create_server_run(self.test_scenario.name, [tsu1, tsu2])

    def get_user_key(self):
        call = self.app.post(reverse('apiv1_auth:rest_login'), params=collections.OrderedDict([
            ('username', get_username()),
            ('password', 'password')]))
        key = get_object(call.body)['key']
        head = {'Authorization': 'Token {}'.format(key)}
        return head

    def test_unauthenticated_user(self):
        call = self.app.get(reverse('apiv1session:session_types-list'), expect_errors=True)

    def test_creation_server_run(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, headers=self.get_user_key())

    def test_full_stack(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, headers=self.get_user_key())
        call = call.json
        self.assertEqual(call['secret'], self.server_run['secret'])
        self.server_run['pk'] = call['id']
        call = self.app.get(reverse('apiv1server:provider:api_server-run-detail', kwargs={
            'pk': self.server_run['pk']
        }), headers=self.get_user_key())
        call = call.json
        self.assertEqual(call['status'], 'stopped')
        call = self.app.get(reverse('apiv1server:provider_result', kwargs={
            'pk': self.server_run['pk']
        }), headers=self.get_user_key())
        ptr = PostmanTestResult.objects.filter(postman_test__test_scenario=self.test_scenario.pk).first()
        self.assertEqual(call.json[0]['status'], ptr.status)

    def test_retrieve_server_run(self):
        headers = self.get_user_key()
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, headers=headers)
        parsed = get_object(call.body)
        call = self.app.get(reverse('apiv1server:provider:api_server-run-detail', kwargs={'pk': parsed['id']}).format(parsed['id']), headers=headers)

    def test_data_integrity(self):
        fake_pk = 999

        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, headers=self.get_user_key())
        parsed = get_object(call.body)
        self.assertNotEqual(parsed['id'], fake_pk)

    def test_creation_server_run_auth(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, expect_errors=True)


class TestNoAssertion(TransactionWebTest):

    def setUp(self):
        self.postman_test = PostmanTestNoAssertionFactory()
        self.server_run = create_server_run(self.postman_test.test_scenario.name, [])

    def get_user_key(self):
        call = self.app.post(reverse('apiv1_auth:rest_login'), params=collections.OrderedDict([
            ('username', get_username()),
            ('password', 'password')]))
        key = get_object(call.body)['key']
        head = {'Authorization': 'Token {}'.format(key)}
        return head

    def _test_creation(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, headers=self.get_user_key())
        call = call.json
        self.server_run['pk'] = call['id']
        self.assertEqual(call['test_scenario'], self.server_run['test_scenario'])

    def test_retrieve(self):
        self._test_creation()
        call = self.app.get(reverse('apiv1server:provider:api_server-run-detail', kwargs={
            'pk': self.server_run['pk']
        }), headers=self.get_user_key())
        call = call.json
        self.assertEqual(call['status'], 'stopped')


class ServerValidationHiddenVarsTests(TransactionWebTest):

    list_url = reverse('apiv1server:provider:api_server-run-list')

    def setUp(self):
        self.user = UserFactory.create()
        self.test_scenario = PostmanTestFactory().test_scenario

    def test_api_replace_hidden_vars_with_placeholders(self):
        tsu1 = TestScenarioUrlFactory(hidden=True, test_scenario=self.test_scenario, name='tsu1')
        tsu2 = TestScenarioUrlFactory(hidden=False, test_scenario=self.test_scenario, name='tsu2')
        server_run = ServerRunFactory.create(test_scenario=self.test_scenario, user=self.user)
        _ = EndpointFactory(test_scenario_url=tsu1, server_run=server_run, url='https://url1.com/')
        _ = EndpointFactory(test_scenario_url=tsu2, server_run=server_run, url='https://url2.com/')
        response = self.app.get(self.list_url, user=self.user).json

        self.assertEqual(len(response), 1)

        self.assertEqual(len(response[0]['endpoints']), 2)

        endpoint1, endpoint2 = response[0]['endpoints']
        self.assertEqual(endpoint1['url'], '(hidden)')
        self.assertEqual(endpoint1['test_scenario_url']['name'], 'tsu1')

        self.assertEqual(endpoint2['url'], 'https://url2.com/')
        self.assertEqual(endpoint2['test_scenario_url']['name'], 'tsu2')


class PostmanTestAPITests(TransactionWebTest):

    def setUp(self):
        self.user = UserFactory.create()

        self.postman_tests1 = PostmanTestFactory.create(name='postman_tests', version='1.0.0')
        self.postman_tests2 = PostmanTestFactory.create(name='postman_tests', version='1.0.1')
        PostmanTestFactory.create(name='different_tests', version='1.0.0')

    def test_get_all_versions(self):
        get_versions_url = reverse('apiv1server:provider:api_postman-test-get-all-versions', kwargs={
            'name': 'postman_tests'
        })
        response = self.app.get(get_versions_url, user=self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json), 2)

        self.assertEqual(response.json[0]['name'], 'postman_tests')
        self.assertEqual(response.json[0]['version'], '1.0.0')
        self.assertIn(self.postman_tests1.validation_file.file.name, response.json[0]['validation_file'])

        self.assertEqual(response.json[1]['name'], 'postman_tests')
        self.assertEqual(response.json[1]['version'], '1.0.1')
        self.assertIn(self.postman_tests2.validation_file.file.name, response.json[1]['validation_file'])

    def test_get_all_versions_empty(self):
        get_versions_url = reverse('apiv1server:provider:api_postman-test-get-all-versions', kwargs={
            'name': 'some_non_existent_test'
        })
        response = self.app.get(get_versions_url, user=self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json, [])

    def test_get_specific_version(self):
        get_versions_url = reverse('apiv1server:provider:api_postman-test-get-specific-version', kwargs={
            'name': 'postman_tests',
            'version': '1.0.1'
        })
        response = self.app.get(get_versions_url, user=self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json, self.postman_tests2.valid_file)

    def test_get_specific_version_404(self):
        get_versions_url = reverse('apiv1server:provider:api_postman-test-get-specific-version', kwargs={
            'name': 'some_non_existent_test',
            'version': '1.0.0'
        })
        response = self.app.get(get_versions_url, user=self.user, status='*')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
