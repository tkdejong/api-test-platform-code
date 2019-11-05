from django_webtest import WebTest
from django.urls import reverse

from guardian.shortcuts import assign_perm
from vng.testsession.tests.factories import UserFactory
from vng.servervalidation.models import (
    PostmanTest, TestScenario, TestScenarioUrl
)

from .factories import (
    TestScenarioFactory, TestScenarioUrlFactory, PostmanTestFactory,
    UserFactory, APIFactory
)


class TestScenarioCreateTests(WebTest):

    def setUp(self):
        self.api = APIFactory.create(name="ZGW")
        self.user = UserFactory.create()
        assign_perm("create_scenario_for_api", self.user, self.api)

    def test_create_without_variables(self):
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        form = response.forms[1]
        form['name'] = 'some scenario name'
        form['description'] = 'test description'
        form['public_logs'] = False

        response = form.submit().follow()

        scenario = TestScenario.objects.first()
        self.assertEqual(scenario.name, 'some scenario name')
        self.assertEqual(scenario.description, 'test description')
        self.assertEqual(scenario.public_logs, False)

        scenario_detail_path = reverse('server_run:testscenario-detail', kwargs={
            'api_id': self.api.id,
            'pk': scenario.pk
        })
        self.assertEqual(scenario_detail_path, response.request.path)

    def test_create_scenario_name_already_exists(self):
        TestScenarioFactory.create(name='exists')
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        form = response.forms[1]
        form['name'] = 'exists'
        form['description'] = 'test description'
        form['public_logs'] = False

        response = form.submit()

        scenario_detail_path = reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        })
        self.assertEqual(scenario_detail_path, response.request.path)

    def test_create_with_variable(self):
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        form = response.forms[1]
        form['name'] = 'some scenario name'
        form['description'] = 'test description'
        form['public_logs'] = False

        form['testscenariourl_set-0-name'] = 'token'
        form['testscenariourl_set-0-url'] = False
        form['testscenariourl_set-0-hidden'] = True
        form['testscenariourl_set-0-placeholder'] = 'bearer token'

        response = form.submit().follow()

        scenario = TestScenario.objects.first()
        self.assertEqual(scenario.name, 'some scenario name')
        self.assertEqual(scenario.description, 'test description')
        self.assertEqual(scenario.public_logs, False)

        scenario_detail_path = reverse('server_run:testscenario-detail', kwargs={
            'api_id': self.api.id,
            'pk': scenario.pk
        })
        self.assertEqual(scenario_detail_path, response.request.path)

        variable = TestScenarioUrl.objects.first()
        self.assertEqual(variable.name, 'token')
        self.assertEqual(variable.url, False)
        self.assertEqual(variable.hidden, True)
        self.assertEqual(variable.placeholder, 'bearer token')
        self.assertEqual(variable.test_scenario, scenario)

    def test_create_with_postman_test(self):
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        form = response.forms[1]
        form['name'] = 'some scenario name'
        form['description'] = 'test description'
        form['public_logs'] = False

        form['postmantest_set-0-name'] = 'sometestscript'
        form['postmantest_set-0-version'] = '1.0.2'

        upload_file = open('.gitignore', 'rb')
        form['postmantest_set-0-validation_file'] = [upload_file.name, b'{}']

        form['postmantest_set-0-published_url'] = 'https://example.com'

        response = form.submit().follow()

        scenario = TestScenario.objects.first()
        self.assertEqual(scenario.name, 'some scenario name')
        self.assertEqual(scenario.description, 'test description')
        self.assertEqual(scenario.public_logs, False)

        scenario_detail_path = reverse('server_run:testscenario-detail', kwargs={
            'api_id': self.api.id,
            'pk': scenario.pk
        })
        self.assertEqual(scenario_detail_path, response.request.path)

        postman_test = PostmanTest.objects.first()
        self.assertEqual(postman_test.name, 'sometestscript')
        self.assertEqual(postman_test.version, '1.0.2')
        self.assertTrue(postman_test.validation_file)
        self.assertEqual(postman_test.published_url, 'https://example.com')
        self.assertEqual(postman_test.test_scenario, scenario)

    def test_view_create_page_with_permission(self):
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertEqual(response.status_code, 200)

    def test_view_create_page_with_permission_for_different_api(self):
        user = UserFactory.create()
        api2 = APIFactory.create(name='ATP API')
        assign_perm("create_scenario_for_api", user, api2)
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), user=user, status=[403])

        self.assertEqual(response.status_code, 403)

    def test_view_create_page_without_permission(self):
        user = UserFactory.create()
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), user=user, status=[403])

        self.assertEqual(response.status_code, 403)

    def test_configure_button_visible_for_user_with_permission(self):
        response = self.app.get(reverse('server_run:environment_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertIn('Configure test scenarios', response.text)

    def test_configure_button_invisible_for_user_with_permission_for_different_api(self):
        user = UserFactory.create()
        api2 = APIFactory.create(name='ATP API')
        assign_perm("create_scenario_for_api", user, api2)
        response = self.app.get(reverse('server_run:environment_list', kwargs={
            'api_id': self.api.id
        }), user=user)

        self.assertNotIn('Configure test scenarios', response.text)

    def test_configure_button_invisible_for_user_without_permission(self):
        user = UserFactory.create()
        response = self.app.get(reverse('server_run:environment_list', kwargs={
            'api_id': self.api.id
        }), user=user)

        self.assertNotIn('Configure test scenarios', response.text)
