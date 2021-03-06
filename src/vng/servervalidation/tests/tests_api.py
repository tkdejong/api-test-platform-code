import collections
import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from django_webtest import TransactionWebTest, WebTest
from django.urls import reverse

from rest_framework import status
from vng.accounts.models import User
from vng.postman.choices import ResultChoices
from vng.utils.choices import StatusChoices

from ..models import PostmanTestResult
from .factories import (
    ServerRunFactory, TestScenarioFactory, TestScenarioUrlFactory, PostmanTestFactory,
    PostmanTestNoAssertionFactory, EndpointFactory, PostmanTestResultFactory, EnvironmentFactory,
    PostmanTestResultFailureFactory, PostmanTestResultFailedCallFactory
)
from ...utils.factories import UserFactory


def get_object(r):
    return json.loads(r.decode('utf-8'))


def get_username():
    l = User.objects.all()
    if len(l) != 0:
        return l.first().username
    return UserFactory().username


def create_server_run(name, tsu, env_name='environment1'):
    endpoints = []
    for t in tsu:
        endpoints.append({
            'name': t.name,
            'value': 'https://google.com',
        })
    return {
        'test_scenario': name,
        'client_id': 'client_id_field',
        'secret': 'secret_field',
        'build_version': '123456789',
        'environment': {
            'name': env_name,
            'endpoints': endpoints
        }
    }


class RetrieveCreationTest(TransactionWebTest):

    def setUp(self):
        self.user = UserFactory.create()
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
            ('username', self.user.username),
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
        self.assertEqual(call['build_version'], self.server_run['build_version'])

        self.server_run['uuid'] = call['uuid']
        call = self.app.get(reverse('apiv1server:provider:api_server-run-detail', kwargs={
            'uuid': self.server_run['uuid']
        }), headers=self.get_user_key())
        call = call.json
        self.assertEqual(call['status'], 'stopped')
        call = self.app.get(reverse('apiv1server:provider_result', kwargs={
            'uuid': self.server_run['uuid']
        }), headers=self.get_user_key())
        ptr = PostmanTestResult.objects.filter(postman_test__test_scenario=self.test_scenario.pk).first()
        ptr_status = ResultChoices.success if ptr.is_success() == 1 else ResultChoices.failed
        self.assertEqual(call.json[0]['status'], ptr_status)

    def test_retrieve_server_run(self):
        headers = self.get_user_key()
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, headers=headers)
        parsed = get_object(call.body)
        call = self.app.get(reverse('apiv1server:provider:api_server-run-detail', kwargs={'uuid': parsed['uuid']}).format(parsed['uuid']), headers=headers)

    def test_data_integrity(self):
        fake_pk = 999

        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, headers=self.get_user_key())
        parsed = get_object(call.body)
        self.assertNotEqual(parsed['uuid'], fake_pk)

    def test_creation_server_run_auth(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run, expect_errors=True)


class TestNoAssertion(TransactionWebTest):

    def setUp(self):
        self.user = UserFactory.create()
        self.postman_test = PostmanTestNoAssertionFactory()
        self.test_scenario = self.postman_test.test_scenario
        self.environment = EnvironmentFactory.create(
            test_scenario=self.test_scenario,
            name='environment2',
            user=self.user
        )
        self.tsu = TestScenarioUrlFactory(test_scenario=self.test_scenario)
        self.server_run1 = create_server_run(self.test_scenario.name, [], env_name=self.environment.name)
        self.server_run2 = create_server_run(self.test_scenario.name, [self.tsu])

    def get_user_key(self):
        call = self.app.post(reverse('apiv1_auth:rest_login'), params=collections.OrderedDict([
            ('username', self.user.username),
            ('password', 'password')]))
        key = get_object(call.body)['key']
        head = {'Authorization': 'Token {}'.format(key)}
        return head

    def _test_creation(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run1, headers=self.get_user_key())
        call = call.json
        self.server_run1['uuid'] = call['uuid']
        self.assertEqual(call['test_scenario'], self.server_run1['test_scenario'])

    def test_creation_new_env(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run2, headers=self.get_user_key())
        call = call.json
        self.server_run2['uuid'] = call['uuid']
        self.assertEqual(call['test_scenario'], self.server_run2['test_scenario'])

    def test_creation_existing_env(self):
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), self.server_run1, headers=self.get_user_key())
        call = call.json
        self.server_run1['uuid'] = call['uuid']
        self.assertEqual(call['test_scenario'], self.server_run1['test_scenario'])

    def test_retrieve(self):
        self._test_creation()
        call = self.app.get(reverse('apiv1server:provider:api_server-run-detail', kwargs={
            'uuid': self.server_run1['uuid']
        }), headers=self.get_user_key())
        call = call.json
        self.assertEqual(call['status'], 'stopped')


class ServerValidationHiddenVarsTests(TransactionWebTest):

    def setUp(self):
        self.user, self.user2 = UserFactory.create_batch(2)
        self.test_scenario = PostmanTestFactory().test_scenario

        self.environment = EnvironmentFactory.create()

        tsu1 = TestScenarioUrlFactory(hidden=True, test_scenario=self.test_scenario, name='tsu1')
        tsu2 = TestScenarioUrlFactory(hidden=False, test_scenario=self.test_scenario, name='tsu2')
        self.server_run = ServerRunFactory.create(test_scenario=self.test_scenario, user=self.user, environment=self.environment)
        _ = EndpointFactory(test_scenario_url=tsu1, server_run=self.server_run, url='https://url1.com/', environment=self.environment)
        _ = EndpointFactory(test_scenario_url=tsu2, server_run=self.server_run, url='https://url2.com/', environment=self.environment)

        self.detail_url = reverse('apiv1server:provider:api_server-run-detail', kwargs={'uuid': self.server_run.uuid})


    def test_api_provider_run_not_accessible_for_other_user(self):
        response = self.app.get(self.detail_url, user=self.user2, status=[404])

        self.assertEqual(response.status_code, 404)

    def test_api_show_hidden_vars_for_same_user(self):
        response = self.app.get(self.detail_url, user=self.user).json

        self.assertEqual(len(response['environment']['endpoints']), 2)

        endpoint1, endpoint2 = response['environment']['endpoints']
        self.assertEqual(endpoint1['value'], 'https://url1.com/')
        self.assertEqual(endpoint1['name'], 'tsu1')

        self.assertEqual(endpoint2['value'], 'https://url2.com/')
        self.assertEqual(endpoint2['name'], 'tsu2')


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
        self.assertIn(self.postman_tests1.validation_file.name, response.json[0]['validation_file'])

        self.assertEqual(response.json[1]['name'], 'postman_tests')
        self.assertEqual(response.json[1]['version'], '1.0.1')
        self.assertIn(self.postman_tests2.validation_file.name, response.json[1]['validation_file'])

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


class ServerRunLatestBadgeAPITests(TransactionWebTest):
    def setUp(self):
        self.user1, self.user2 = UserFactory.create_batch(2)
        self.environment1 = EnvironmentFactory.create(user=self.user1)
        self.environment2 = EnvironmentFactory.create(user=self.user2)
        self.environment3 = EnvironmentFactory.create(user=self.user1)
        self.environment4 = EnvironmentFactory.create(user=self.user1)
        self.test_scenario1 = TestScenarioFactory.create(name='ZGW api tests')
        self.test_scenario2 = TestScenarioFactory.create(name='ZGW oas tests')
        self.test_scenario3 = TestScenarioFactory.create(name='APT tests')
        self.server_run1 = ServerRunFactory.create(
            test_scenario=self.test_scenario1, stopped='2019-01-01T12:00:00Z',
            user=self.user1, environment=self.environment1
        )
        self.server_run2 = ServerRunFactory.create(
            test_scenario=self.test_scenario1, stopped='2019-01-01T13:00:00Z',
            user=self.user1, environment=self.environment1
        )
        self.server_run3 = ServerRunFactory.create(
            test_scenario=self.test_scenario1, stopped='2019-01-01T14:00:00Z',
            user=self.user2, environment=self.environment2
        )
        self.server_run4 = ServerRunFactory.create(
            test_scenario=self.test_scenario2, stopped='2019-01-01T14:00:00Z',
            user=self.user1, environment=self.environment3
        )
        self.server_run5 = ServerRunFactory.create(
            test_scenario=self.test_scenario1, stopped='2019-01-01T12:00:00Z',
            user=self.user1, environment=self.environment4
        )
        PostmanTestResultFactory.create(server_run=self.server_run1, status=ResultChoices.failed)
        PostmanTestResultFactory.create(server_run=self.server_run2, status=ResultChoices.success)
        PostmanTestResultFactory.create(server_run=self.server_run3, status=ResultChoices.failed)
        PostmanTestResultFailureFactory.create(server_run=self.server_run4, status=ResultChoices.failed)
        PostmanTestResultFactory.create(server_run=self.server_run5, status=ResultChoices.failed)

    def test_get_latest_success(self):
        get_badge_url = reverse('apiv1server:latest-badge', kwargs={
            'uuid': self.environment1.uuid
        })
        response = self.app.get(get_badge_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json
        expected_response = {
            'schemaVersion': 1,
            'label': 'API Test Platform',
            'message': 'Success',
            'color': 'green',
            'isError': False
        }
        self.assertDictEqual(data, expected_response)

    def test_get_latest_failure(self):
        get_badge_url = reverse('apiv1server:latest-badge', kwargs={
            'uuid': self.environment3.uuid
        })
        response = self.app.get(get_badge_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json
        expected_response = {
            'schemaVersion': 1,
            'label': 'API Test Platform',
            'message': 'Failed',
            'color': 'red',
            'isError': True
        }
        self.assertDictEqual(data, expected_response)

    def test_get_latest_404(self):
        environment = EnvironmentFactory.create()
        get_badge_url = reverse('apiv1server:latest-badge', kwargs={
            'uuid': environment.uuid
        })
        response = self.app.get(get_badge_url, status='*')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_badge_success_with_failing_request(self):
        server_run = ServerRunFactory.create(
            test_scenario=self.test_scenario1, stopped='2019-01-01T12:00:00Z',
            user=self.user1, environment=self.environment4
        )
        ptr = PostmanTestResultFailedCallFactory.create(server_run=server_run, status=ResultChoices.success)

        call_results = ptr.get_aggregate_results()

        self.assertEqual(call_results["assertions"]["passed"], 1)
        self.assertEqual(call_results["assertions"]["failed"], 0)

        # Call only fails if one or more assertions for that call fail
        self.assertEqual(call_results["calls"]["failed"], 0)

        get_badge_url = reverse('apiv1server:latest-badge', kwargs={
            'uuid': self.environment4.uuid
        })
        response = self.app.get(get_badge_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json
        expected_response = {
            'schemaVersion': 1,
            'label': 'API Test Platform',
            'message': 'Success',
            'color': 'green',
            'isError': False
        }
        self.assertDictEqual(data, expected_response)


class EnvironmentAPITests(TransactionWebTest):

    def setUp(self):
        self.user1, self.user2 = UserFactory.create_batch(2)
        self.test_scenario = TestScenarioFactory.create(name='ZGW api tests')
        self.tsu = TestScenarioUrlFactory(test_scenario=self.test_scenario, name='url', placeholder='https://google.com/')
        self.environment1 = EnvironmentFactory.create(user=self.user1, name='test', test_scenario=self.test_scenario)
        self.environment2 = EnvironmentFactory.create(user=self.user2, name='test2', test_scenario=self.test_scenario)
        EndpointFactory.create(environment=self.environment1, test_scenario_url=self.tsu, url='https://example.com/')
        EndpointFactory.create(environment=self.environment2, test_scenario_url=self.tsu, url='https://example2.com/')

    def get_user_key(self):
        call = self.app.post(reverse('apiv1_auth:rest_login'), params=collections.OrderedDict([
            ('username', self.user1.username),
            ('password', 'password')]))
        key = get_object(call.body)['key']
        head = {'Authorization': 'Token {}'.format(key)}
        return head

    def test_create_server_run_with_new_env(self):
        body = create_server_run(self.test_scenario.name, [self.tsu], env_name='newenv')
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), body, headers=self.get_user_key())
        call = call.json
        body['uuid'] = call['uuid']
        self.assertEqual(call['test_scenario'], self.test_scenario.name)
        self.assertEqual(call['environment']['name'], 'newenv')

        endpoint = call['environment']['endpoints'][0]
        self.assertEqual(endpoint['name'], 'url')

    def test_create_server_run_with_existing_env(self):
        body = create_server_run(self.test_scenario.name, [], env_name='test')
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), body, headers=self.get_user_key())
        call = call.json
        body['uuid'] = call['uuid']
        self.assertEqual(call['test_scenario'], self.test_scenario.name)
        self.assertEqual(call['environment']['name'], 'test')
        self.assertEqual(call['environment']['uuid'], str(self.environment1.uuid))

        endpoint = call['environment']['endpoints'][0]
        self.assertEqual(endpoint['name'], 'url')

    def test_create_server_run_with_existing_env_and_new_endpoints(self):
        body = create_server_run(self.test_scenario.name, [self.tsu], env_name='test')
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), body, headers=self.get_user_key(), status='*')
        call = call.json
        body['uuid'] = call['uuid']
        self.assertEqual(call['test_scenario'], self.test_scenario.name)
        self.assertEqual(call['environment']['name'], 'test')
        self.assertEqual(call['environment']['uuid'], str(self.environment1.uuid))

        endpoint = call['environment']['endpoints'][0]
        self.assertEqual(endpoint['name'], 'url')

    def test_create_server_run_with_new_env_with_same_name_as_env_for_different_user(self):
        body = create_server_run(self.test_scenario.name, [self.tsu], env_name='test2')
        call = self.app.post_json(reverse('apiv1server:provider:api_server-run-list'), body, headers=self.get_user_key(), status='*')
        call = call.json
        body['uuid'] = call['uuid']
        self.assertEqual(call['test_scenario'], self.test_scenario.name)
        self.assertEqual(call['environment']['name'], 'test2')

        endpoint = call['environment']['endpoints'][0]
        self.assertEqual(endpoint['name'], 'url')


class ServerRunResultAPITests(WebTest):

    def setUp(self):
        self.user = UserFactory.create()
        self.environment = EnvironmentFactory.create(user=self.user)
        self.test_scenario = TestScenarioFactory.create(name='ZGW api tests')
        self.server_run = ServerRunFactory.create(
            test_scenario=self.test_scenario, stopped='2019-01-01T12:00:00Z',
            user=self.user, environment=self.environment, status=StatusChoices.stopped
        )

    def test_get_result_request_without_response(self):
        postman_result = PostmanTestResultFactory.create(server_run=self.server_run, status=ResultChoices.failed)
        with open(postman_result.log_json.path, 'w') as f:
            json.dump(
                {
                    'run': {
                        'executions': [
                            {
                                'item': {'name': 'no response'},
                                'request': {'method': 'GET', 'url': 'https://some-url.com'}
                            }
                        ],
                        'timings': {'started': '100', 'stopped': '200'}
                    }
                },
                f
            )

        response = self.app.get(reverse('apiv1server:provider_result', kwargs={
            'uuid': self.server_run.uuid
        }), user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['status'], ResultChoices.success)
        self.assertEqual(response.json[0]['calls'][0]['status'], 'Error')

    def test_get_result_request_with_response(self):
        postman_result = PostmanTestResultFactory.create(server_run=self.server_run, status=ResultChoices.success)
        with open(postman_result.log_json.path, 'w') as f:
            json.dump(
                {
                    'run': {
                        'executions': [
                            {
                                'item': {'name': 'response'},
                                'request': {'method': 'GET', 'url': 'https://some-url.com'},
                                'response': {'code': 200}
                            }
                        ],
                        'timings': {'started': '100', 'stopped': '200'}
                    }
                },
                f
            )

        response = self.app.get(reverse('apiv1server:provider_result', kwargs={
            'uuid': self.server_run.uuid
        }), user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['status'], ResultChoices.success)
        self.assertEqual(response.json[0]['calls'][0]['status'], 'Success')

    def test_get_result_no_status_on_result(self):
        postman_result = PostmanTestResultFactory.create(server_run=self.server_run, status=None)
        with open(postman_result.log_json.path, 'w') as f:
            json.dump(
                {
                    'run': {
                        'executions': [
                            {
                                'item': {'name': 'no response'},
                                'request': {'method': 'GET', 'url': 'https://some-url.com'},
                                'assertions': [{'error': 'bla'}, {}]
                            }
                        ],
                        'timings': {'started': '100', 'stopped': '200'}
                    }
                },
                f
            )

        response = self.app.get(reverse('apiv1server:provider_result', kwargs={
            'uuid': self.server_run.uuid
        }), user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['status'], ResultChoices.failed)
