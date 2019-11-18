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


class TestScenarioListTests(WebTest):

    def setUp(self):
        self.api = APIFactory.create(name="ZGW")
        self.test_scenario = TestScenarioFactory.create(api=self.api)
        self.user = UserFactory.create()
        assign_perm("list_scenario_for_api", self.user, self.api)

    def test_create_button_visible_for_user_with_permission(self):
        assign_perm("create_scenario_for_api", self.user, self.api)
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertIn('Create new test scenario', response.text)

    def test_create_button_invisible_for_user_with_permission_for_different_api(self):
        api2 = APIFactory.create(name='ATP API')
        assign_perm("create_scenario_for_api", self.user, api2)
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertNotIn('Create new test scenario', response.text)

    def test_create_button_invisible_for_user_without_permission_to_create(self):
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertNotIn('Create new test scenario', response.text)

    def test_delete_button_visible_for_user_with_permission(self):
        assign_perm("delete_scenario_for_api", self.user, self.api)
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertIn('Delete', response.text)

    def test_delete_button_invisible_for_user_with_permission_for_different_api(self):
        api2 = APIFactory.create(name='ATP API')
        assign_perm("delete_scenario_for_api", self.user, api2)
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertNotIn('Delete', response.text)

    def test_delete_button_invisible_for_user_without_permission_to_delete(self):
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertNotIn('Delete', response.text)

    def test_update_button_visible_for_user_with_permission(self):
        assign_perm("update_scenario_for_api", self.user, self.api)
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertIn('Update', response.text)

    def test_update_button_invisible_for_user_with_permission_for_different_api(self):
        api2 = APIFactory.create(name='ATP API')
        assign_perm("update_scenario_for_api", self.user, api2)
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertNotIn('Update', response.text)

    def test_update_button_invisible_for_user_without_permission_to_update(self):
        response = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertNotIn('Update', response.text)


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
        }), {"extra": 1}, user=self.user)

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
        }), {"extra": 1}, user=self.user)

        form = response.forms[1]
        form['name'] = 'some scenario name'
        form['description'] = 'test description'
        form['public_logs'] = False

        form['postmantest_set-0-name'] = 'sometestscript'
        form['postmantest_set-0-version'] = '1.0.2'

        upload_file = open('README.md', 'rb')
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
        assign_perm("list_scenario_for_api", self.user, self.api)
        response = self.app.get(reverse('server_run:environment_list', kwargs={
            'api_id': self.api.id
        }), user=self.user)

        self.assertIn('Configure test scenarios', response.text)

    def test_configure_button_invisible_for_user_with_permission_for_different_api(self):
        user = UserFactory.create()
        api2 = APIFactory.create(name='ATP API')
        assign_perm("list_scenario_for_api", user, api2)
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

    def test_create_postman_test_file_validation(self):
        response = self.app.get(reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.api.id
        }), {"extra": 1}, user=self.user)

        form = response.forms[1]
        form['name'] = 'some scenario name'
        form['description'] = 'test description'
        form['public_logs'] = False

        form['postmantest_set-0-name'] = 'sometestscript'
        form['postmantest_set-0-version'] = '1.0.2'

        form['postmantest_set-0-published_url'] = 'https://example.com'

        response = form.submit()

        error_div = response.html.find('p', {'id': 'error_1_id_postmantest_set-0-validation_file'})
        self.assertIn('required', error_div.text)


class TestScenarioUpdateTests(WebTest):

    def setUp(self):
        self.api = APIFactory.create(name="ZGW")
        self.test_scenario = TestScenarioFactory.create(name="API tests", description="bla")
        self.test_scenario_url = TestScenarioUrlFactory.create(name="token", test_scenario=self.test_scenario)
        self.postman_test = PostmanTestFactory.create(test_scenario=self.test_scenario)
        self.user = UserFactory.create()
        assign_perm("update_scenario_for_api", self.user, self.api)
        assign_perm("list_scenario_for_api", self.user, self.api)

    def test_update_test_scenario_same_name_no_validation_error_unique(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=self.user)

        form = response.forms[1]

        response = form.submit().follow()

        self.assertEqual(response.status_code, 200)

    def test_update_test_scenario_modify_data(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=self.user)

        form = response.forms[1]
        form['name'] = 'changed'
        form['description'] = 'test description'
        form['public_logs'] = False
        form['active'] = True

        response = form.submit()

        self.test_scenario.refresh_from_db()

        self.assertEqual(self.test_scenario.name, 'changed')
        self.assertEqual(self.test_scenario.description, 'test description')
        self.assertEqual(self.test_scenario.public_logs, False)
        self.assertEqual(self.test_scenario.active, True)

    def test_update_scenario_update_existing_variable(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=self.user)

        form = response.forms[1]

        form['testscenariourl_set-0-name'] = 'token edited'
        form['testscenariourl_set-0-url'] = False
        form['testscenariourl_set-0-hidden'] = True
        form['testscenariourl_set-0-placeholder'] = 'bearer token'

        response = form.submit()

        self.test_scenario_url.refresh_from_db()
        self.assertEqual(self.test_scenario_url.name, 'token edited')
        self.assertEqual(self.test_scenario_url.url, False)
        self.assertEqual(self.test_scenario_url.hidden, True)
        self.assertEqual(self.test_scenario_url.placeholder, 'bearer token')

    def test_update_scenario_add_new_variable(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), {"extra": 1}, user=self.user)

        number_of_vars = self.test_scenario.testscenariourl_set.count()

        form = response.forms[1]

        form['testscenariourl_set-1-name'] = 'newvar'
        form['testscenariourl_set-1-url'] = True
        form['testscenariourl_set-1-hidden'] = False
        form['testscenariourl_set-1-placeholder'] = 'https://example.com'

        response = form.submit()

        self.assertEqual(self.test_scenario.testscenariourl_set.count(), number_of_vars + 1)

        test_scenario_url = TestScenarioUrl.objects.get(name="newvar")
        self.assertEqual(test_scenario_url.name, 'newvar')
        self.assertEqual(test_scenario_url.url, True)
        self.assertEqual(test_scenario_url.hidden, False)
        self.assertEqual(test_scenario_url.placeholder, 'https://example.com')

    def test_update_scenario_update_existing_postman_test(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=self.user)

        form = response.forms[1]

        form['postmantest_set-0-name'] = 'sometestscript'
        form['postmantest_set-0-version'] = '1.0.2'

        upload_file = open('README.md', 'rb')
        form['postmantest_set-0-validation_file'] = [upload_file.name, b'{}']

        form['postmantest_set-0-published_url'] = 'https://example.com'

        response = form.submit().follow()

        self.postman_test.refresh_from_db()
        self.assertEqual(self.postman_test.name, 'sometestscript')
        self.assertEqual(self.postman_test.version, '1.0.2')
        self.assertTrue(self.postman_test.validation_file)
        self.assertEqual(self.postman_test.published_url, 'https://example.com')

    def test_update_scenario_add_new_postman_test(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), {"extra": 1}, user=self.user)

        number_of_tests = self.test_scenario.postmantest_set.count()

        form = response.forms[1]

        form['postmantest_set-1-name'] = 'newscript'
        form['postmantest_set-1-version'] = '2.0.0'

        upload_file = open('README.md', 'rb')
        form['postmantest_set-1-validation_file'] = [upload_file.name, b'{}']

        form['postmantest_set-1-published_url'] = 'https://google.com'

        response = form.submit().follow()

        self.assertEqual(self.test_scenario.postmantest_set.count(), number_of_tests + 1)

        postman_test = PostmanTest.objects.get(name='newscript')
        self.assertEqual(postman_test.name, 'newscript')
        self.assertEqual(postman_test.version, '2.0.0')
        self.assertTrue(postman_test.validation_file)
        self.assertEqual(postman_test.published_url, 'https://google.com')

    def test_update_scenario_delete_existing_variable(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), {"extra": 1}, user=self.user)

        form = response.forms[1]

        form['testscenariourl_set-0-DELETE'] = True

        response = form.submit()

        self.assertEqual(self.test_scenario.testscenariourl_set.count(), 0)

    def test_update_scenario_delete_existing_postmantest(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), {"extra": 1}, user=self.user)

        form = response.forms[1]

        form['postmantest_set-0-DELETE'] = True

        response = form.submit().follow()

        self.assertEqual(self.test_scenario.postmantest_set.count(), 0)

    def test_view_update_page_with_permission(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=self.user)

        self.assertEqual(response.status_code, 200)

    def test_view_update_page_with_permission_for_different_api(self):
        user = UserFactory.create()
        api2 = APIFactory.create(name='ATP API')
        assign_perm("update_scenario_for_api", user, api2)
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=user, status=[403])

        self.assertEqual(response.status_code, 403)

    def test_view_update_page_without_permission(self):
        user = UserFactory.create()
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=user, status=[403])

        self.assertEqual(response.status_code, 403)


class TestScenarioDeleteTests(WebTest):

    def setUp(self):
        self.api = APIFactory.create(name="ZGW")
        self.test_scenario = TestScenarioFactory.create(name="API tests", description="bla")
        self.test_scenario_url = TestScenarioUrlFactory.create(name="token", test_scenario=self.test_scenario)
        self.postman_test = PostmanTestFactory.create(test_scenario=self.test_scenario)
        self.user = UserFactory.create()
        assign_perm("delete_scenario_for_api", self.user, self.api)
        assign_perm("list_scenario_for_api", self.user, self.api)

    def test_delete_test_scenario(self):
        response = self.app.get(reverse('server_run:testscenario-delete', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=self.user).follow()

        self.assertEqual(response.status_code, 200)

        self.assertFalse(self.api.testscenario_set.exists())

    def test_delete_with_permission_for_different_api_fails(self):
        user = UserFactory.create()
        api2 = APIFactory.create(name='ATP API')
        assign_perm("update_scenario_for_api", user, api2)
        response = self.app.get(reverse('server_run:testscenario-delete', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=user, status=[403])

        self.assertEqual(response.status_code, 403)

    def test_delete_without_permission_fails(self):
        user = UserFactory.create()
        response = self.app.get(reverse('server_run:testscenario-delete', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), user=user, status=[403])

        self.assertEqual(response.status_code, 403)


class TestScenarioConfigIntegrationTests(WebTest):

    def setUp(self):
        self.api = APIFactory.create(name="ZGW")
        self.test_scenario = TestScenarioFactory.create(name="API tests", description="bla")
        self.test_scenario_url1 = TestScenarioUrlFactory.create(name="token", test_scenario=self.test_scenario)
        self.test_scenario_url2 = TestScenarioUrlFactory.create(name="url", test_scenario=self.test_scenario)
        self.postman_test1 = PostmanTestFactory.create(name="test1", test_scenario=self.test_scenario)
        self.postman_test2 = PostmanTestFactory.create(name="test2", test_scenario=self.test_scenario)
        self.user = UserFactory.create()
        assign_perm("update_scenario_for_api", self.user, self.api)
        assign_perm("list_scenario_for_api", self.user, self.api)

    def test_update_scenario_delete_update_create_variables(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), {'extra': 1}, user=self.user)

        form = response.forms[1]

        # Delete an existing variable
        form['testscenariourl_set-0-DELETE'] = True

        # Update an existing variable
        form['testscenariourl_set-1-name'] = 'updatedvar'
        form['testscenariourl_set-1-url'] = False
        form['testscenariourl_set-1-hidden'] = True
        form['testscenariourl_set-1-placeholder'] = 'token'

        # Add a new variable
        form['testscenariourl_set-2-name'] = 'newvar'
        form['testscenariourl_set-2-url'] = True
        form['testscenariourl_set-2-hidden'] = False
        form['testscenariourl_set-2-placeholder'] = 'https://example.com'

        response = form.submit()

        variables = self.test_scenario.testscenariourl_set.all().order_by('pk')
        self.assertEqual(variables.count(), 2)

        self.test_scenario_url2.refresh_from_db()
        self.assertEqual(self.test_scenario_url2.name, 'updatedvar')
        self.assertEqual(self.test_scenario_url2.url, False)
        self.assertEqual(self.test_scenario_url2.hidden, True)
        self.assertEqual(self.test_scenario_url2.placeholder, 'token')

        new_variable = variables.last()
        self.assertEqual(new_variable.name, 'newvar')
        self.assertEqual(new_variable.url, True)
        self.assertEqual(new_variable.hidden, False)
        self.assertEqual(new_variable.placeholder, 'https://example.com')

    def test_update_scenario_delete_update_create_postman_tests(self):
        response = self.app.get(reverse('server_run:testscenario-update', kwargs={
            'api_id': self.api.id,
            'scenario_uuid': self.test_scenario.uuid
        }), {'extra': 1}, user=self.user)

        form = response.forms[1]

        # Delete an existing Postman test
        form['postmantest_set-0-DELETE'] = True

        # Update an existing Postman test
        form['postmantest_set-1-name'] = 'updatedtest'
        form['postmantest_set-1-version'] = '2.0.0'
        upload_file = open('README.md', 'rb')
        form['postmantest_set-1-validation_file'] = [upload_file.name, b'{}']
        form['postmantest_set-1-published_url'] = 'https://example.com'

        # Add a new Postman test
        form['postmantest_set-2-name'] = 'newtest'
        form['postmantest_set-2-version'] = '1.0.2'
        upload_file = open('README.rst', 'rb')
        form['postmantest_set-2-validation_file'] = [upload_file.name, b'{}']
        form['postmantest_set-2-published_url'] = 'https://google.com'

        response = form.submit().follow()

        postman_tests = self.test_scenario.postmantest_set.all().order_by('pk')
        self.assertEqual(postman_tests.count(), 2)

        self.postman_test2.refresh_from_db()
        self.assertEqual(self.postman_test2.name, 'updatedtest')
        self.assertEqual(self.postman_test2.version, '2.0.0')
        self.assertTrue(self.postman_test2.validation_file)
        self.assertEqual(self.postman_test2.published_url, 'https://example.com')

        new_test = postman_tests.last()
        self.assertEqual(new_test.name, 'newtest')
        self.assertEqual(new_test.version, '1.0.2')
        self.assertTrue(new_test.validation_file)
        self.assertEqual(new_test.published_url, 'https://google.com')
