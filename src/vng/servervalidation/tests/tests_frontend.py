import factory
import json

from django_webtest import WebTest
from django.urls import reverse

from vng.testsession.tests.factories import UserFactory
from vng.servervalidation.models import ServerRun, PostmanTest, PostmanTestResult, User, ScheduledTestScenario

from .factories import (
    TestScenarioFactory, ServerRunFactory, TestScenarioUrlFactory, PostmanTestFactory,
    UserFactory, PostmanTestSubFolderFactory, EndpointFactory, PostmanTestResultFactory,
    EnvironmentFactory, ScheduledTestScenarioFactory, APIFactory
)
from ...utils import choices, forms


class TestMultipleEndpoint(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.ts = TestScenarioFactory()
        self.ts.authorization = choices.AuthenticationChoices.no_auth
        self.ts.save()
        TestScenarioUrlFactory(test_scenario=self.ts, name='url1')
        TestScenarioUrlFactory(test_scenario=self.ts, name='url2')

    def test_run_collection(self):
        call = self.app.get(reverse('server_run:server-run_create_item', kwargs={
            'api_id': self.ts.api.id
        }), user=self.user)
        form = call.forms[1]
        form['test_scenario'] = self.ts.pk

        res = form.submit().follow()
        form = res.forms[1]
        form['create_env'] = 'created_env_name'

        res = form.submit().follow()

        form = res.forms[1]
        form['url1'] = 'https://ref.tst.vng.cloud/drc/api/v1/'
        form['url2'] = 'https://ref.tst.vng.cloud/zrc/api/v1/'
        form.submit()


class TestCreation(WebTest):

    def setUp(self):
        self.test_scenario = TestScenarioFactory.create()

        self.tsf = TestScenarioUrlFactory(name='url', test_scenario=self.test_scenario)
        self.pt = PostmanTestFactory(test_scenario=self.test_scenario)
        self.user = UserFactory(username='testuser1')

        self.environment = EnvironmentFactory.create(
            name='testenv', test_scenario=self.test_scenario, user=self.user
        )

    def test_creation_error_list(self):
        ServerRunFactory.create(
            test_scenario=self.test_scenario,
            user=self.user,
            environment=self.environment
        )

        call = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': self.test_scenario.uuid,
            'env_uuid': self.environment.uuid
        }), user='test')
        self.assertNotIn('Starting', call.text)

        call = self.app.get(reverse('server_run:server-run_create_item', kwargs={
            'api_id': self.test_scenario.api.id
        }), user='test')
        form = call.forms[1]
        form['test_scenario'].force_value('9')
        form.submit()
        call = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': self.test_scenario.uuid,
            'env_uuid': self.environment.uuid
        }), user='test')
        self.assertNotIn('Starting', call.text)

    def test_scenarios_create_new_env(self):
        call = self.app.get(reverse('server_run:server-run_create_item', kwargs={
            'api_id': self.test_scenario.api.id
        }), user=self.user)
        form = call.forms[1]
        form['test_scenario'] = self.tsf.test_scenario.pk

        res = form.submit().follow()
        form = res.forms[1]
        form['create_env'] = 'created_env_name'

        res = form.submit().follow()
        form = res.forms[1]
        form['url'] = 'https://ref.tst.vng.cloud/drc/api/v1/'
        form['Client ID'] = 'client id'
        form['Secret'] = 'secret'
        form.submit()

        call = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.test_scenario.api.id
        }), user=self.user)
        self.assertIn(self.user.username, call.text)
        self.assertIn(self.test_scenario.name, call.text)
        self.assertIn('created_env_name', call.text)
        server = ServerRun.objects.filter(status=choices.StatusChoices.stopped)[0]

        url = reverse('server_run:server-run_detail', kwargs={
            'uuid': server.uuid
        })
        call = self.app.get(url, user=self.user)

        ptr = PostmanTestResult.objects.get(postman_test__test_scenario=server.test_scenario)
        url = reverse('server_run:server-run_detail_log', kwargs={
            'uuid': ptr.server_run.uuid,
            'test_result_pk': ptr.pk
        })
        call = self.app.get(url, user=self.user)

        ptr = PostmanTestResult.objects.get(postman_test__test_scenario=server.test_scenario)
        url = reverse('server_run:server-run_detail_log_json', kwargs={
            'uuid': ptr.server_run.uuid,
            'test_result_pk': ptr.pk
        })
        call = self.app.get(url, user=self.user)

        ptr = PostmanTestResult.objects.get(postman_test__test_scenario=server.test_scenario)
        url = reverse('server_run:server-run_detail_pdf', kwargs={
            'uuid': server.uuid,
            'test_result_pk': ptr.pk
        })
        call = self.app.get(url, user=self.user)

    def test_scenarios_use_existing_env(self):
        call = self.app.get(reverse('server_run:server-run_create_item', kwargs={
            'api_id': self.test_scenario.api.id
        }), user=self.user)
        form = call.forms[1]
        form['test_scenario'] = self.tsf.test_scenario.pk

        res = form.submit().follow()
        form = res.forms[1]
        form['environment'] = str(self.environment.id)

        res = form.submit().follow()

        call = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.test_scenario.api.id
        }), user=self.user)
        self.assertIn(self.user.username, call.text)
        self.assertIn(self.test_scenario.name, call.text)
        self.assertIn(self.environment.name, call.text)
        server = ServerRun.objects.filter(status=choices.StatusChoices.stopped)[0]

        url = reverse('server_run:server-run_detail', kwargs={
            'uuid': server.uuid
        })
        call = self.app.get(url, user=self.user)

        ptr = PostmanTestResult.objects.get(postman_test__test_scenario=server.test_scenario)
        url = reverse('server_run:server-run_detail_log', kwargs={
            'uuid': ptr.server_run.uuid,
            'test_result_pk': ptr.pk
        })
        call = self.app.get(url, user=self.user)

        ptr = PostmanTestResult.objects.get(postman_test__test_scenario=server.test_scenario)
        url = reverse('server_run:server-run_detail_log_json', kwargs={
            'uuid': ptr.server_run.uuid,
            'test_result_pk': ptr.pk
        })
        call = self.app.get(url, user=self.user)

        ptr = PostmanTestResult.objects.get(postman_test__test_scenario=server.test_scenario)
        url = reverse('server_run:server-run_detail_pdf', kwargs={
            'uuid': server.uuid,
            'test_result_pk': ptr.pk
        })
        call = self.app.get(url, user=self.user)

    def test_postman_outcome(self):
        ServerRunFactory.create(
            test_scenario=self.test_scenario,
            user=self.user,
            environment=self.environment
        )
        server = ServerRun.objects.filter(user=self.user).order_by('-started')[0]
        url = reverse('server_run:server-run_detail', kwargs={
            'uuid': server.uuid
        })
        call = self.app.get(url, user=self.user)
        self.assertIn(str(server.pk), call.text)


class TestList(WebTest):

    def setUp(self):
        self.user = UserFactory.create()
        self.api1, self.api2 = APIFactory.create_batch(2)
        self.test_scenario1 = TestScenarioFactory(name='scenario1', api=self.api1)
        self.test_scenario2 = TestScenarioFactory.create(name='scenario2', api=self.api2)
        ServerRunFactory.create(test_scenario=self.test_scenario1, user=self.user, stopped='2019-01-01T00:00:00Z')
        ServerRunFactory.create(test_scenario=self.test_scenario2, user=self.user, stopped='2019-01-01T00:00:00Z')

    def test_list(self):
        call = self.app.get(reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.api1.id
        }), user=self.user)

        self.assertIn('scenario1', call.text)
        self.assertNotIn('scenario2', call.text)


class TestUserRegistration(WebTest):

    def add_dynamic_field(self, form, name, value):
        from webtest.forms import Text
        field = Text(form, 'input', name, None, value)
        field.id = name
        form.fields[name] = [field]

    def test_registration(self):

        # user registration
        call = self.app.get(reverse('registration_register'))
        form = call.forms[1]
        form['username'] = 'test'
        form['email'] = 'test.gmail.com'
        form['password1'] = 'asdgja3u8lksa'
        form['password2'] = 'asdgja3u8lksa'
        call = form.submit()

        # try to login before email confirmation
        call = self.app.get(reverse('auth_login'))
        form = call.forms[1]
        form['username'] = 'test'
        form['password'] = 'password'
        form.submit(expect_errors=True)

        User.objects.create_user(username='test', password='12345678a').save()
        call = self.app.get(reverse('auth_login'))
        form = call.forms[1]
        form['username'] = 'test'
        form['password'] = '12345678a'
        call = form.submit()
        self.assertIn(call.text, 'consumer')


class IntegrationTest(WebTest):

    def setUp(self):
        self.api1, self.api2 = APIFactory.create_batch(2)
        self.user = UserFactory.create()
        self.server = ServerRunFactory()
        self.test_scenario = TestScenarioFactory.create(name='scenario1', api=self.api1)
        self.test_scenario2 = TestScenarioFactory.create(name='scenario2', api=self.api2)
        TestScenarioUrlFactory.create(name='url', test_scenario=self.test_scenario)
        self.environment = EnvironmentFactory.create(
            test_scenario=self.test_scenario,
            user=self.user
        )
        PostmanTestFactory(test_scenario=self.test_scenario)

    def test_create_provider_run_filters_by_api(self):
        response = self.app.get(reverse('server_run:server-run_create_item', kwargs={
            'api_id': self.api1.id
        }))
        self.assertIn('scenario1', response.text)
        self.assertNotIn('scenario2', response.text)

    def test_access(self):
        server = ServerRunFactory(
            test_scenario=self.test_scenario,
            environment=self.environment,
            user=self.user
        )
        call = self.app.get(reverse('server_run:server-run_detail', kwargs={
            'uuid': server.uuid
        }))
        self.assertIn(str(server.id), call.text)

    def test_trigger(self):
        prev = len(PostmanTestResult.objects.all())
        self.app.get(
            reverse('server_run:server-run_trigger', kwargs={
                'uuid': self.environment.uuid
            }), user=self.user
        )
        self.assertEqual(prev, len(PostmanTestResult.objects.all()) - 1)

    def test_badge(self):
        call = self.app.get(reverse('server_run:server-run_create_item', kwargs={
            'api_id': self.test_scenario.api.id
        }), user=self.user)
        form = call.forms[1]
        form['test_scenario'] = self.test_scenario.pk
        res = form.submit().follow()

        form = res.forms[1]
        form['create_env'] = 'env'
        res = form.submit().follow()

        form = res.forms[1]
        form['url'] = 'https://ref.tst.vng.cloud/drc/api/v1/'
        form['Client ID'] = 'client id'
        form['Secret'] = 'secret'
        form.submit()
        new_server = ServerRun.objects.latest('id')

        call = self.app.get(reverse('server_run:server-run_detail', kwargs={
            'uuid': new_server.uuid
        }))
        self.assertIn(str(new_server.uuid), call.text)
        call = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': new_server.test_scenario.uuid,
            'env_uuid': new_server.environment.uuid
        }), user=self.user)
        ptr = PostmanTestResult.objects.all()[0]
        self.assertIn(str(ptr.get_assertions_details()[0]), call.text)

    def test_session_number_no_user(self):
        server = ServerRunFactory(
            test_scenario=self.test_scenario,
            environment=self.environment,
            user=self.user
        )

        # simply check that with no user it raises no errors
        call = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': server.test_scenario.uuid,
            'env_uuid': server.environment.uuid
        }), status=[200, 302])

    def test_session_number_user(self):
        server = ServerRunFactory(
            test_scenario=self.test_scenario,
            environment=self.environment,
            user=self.user
        )
        call = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': server.test_scenario.uuid,
            'env_uuid': server.environment.uuid
        }), user=self.user)
        self.assertIn(str(ServerRun.objects.filter(user=self.user).count()), call.text)

    def test_information_form(self):
        self.test_badge()
        new_server = ServerRun.objects.latest('id')
        call = self.app.get(
            reverse(
                'server_run:server-run_info-update',
                kwargs={'uuid': new_server.uuid}),
            user=self.user
        )
        form = call.forms[1]
        form['supplier_name'] = 'test_name'
        form['software_product'] = 'test_software'
        form['product_role'] = 'test_product'
        res = form.submit().follow()
        new_server = ServerRun.objects.latest('id')
        self.assertEqual(new_server.product_role, 'test_product')

        call = self.app.get(
            reverse(
                'server_run:server-run_info-update',
                kwargs={'uuid': new_server.uuid}),
            user='random',
            status=[403]
        )

    def test_add_schedule_to_env(self):
        response = self.app.get(reverse('server_run:server-run_create_schedule', kwargs={
            'uuid': self.environment.uuid
        }), user=self.user, auto_follow=True)

        self.assertIn("Scheduled to run", response.text)

        scheduled = ScheduledTestScenario.objects.filter(environment=self.environment)

        self.assertEqual(scheduled.count(), 1)
        self.assertEqual(scheduled.first().active, True)

    def test_deactivate_schedule(self):
        self.app.get(reverse('server_run:server-run_create_schedule', kwargs={
            'uuid': self.environment.uuid
        }), user=self.user)

        response = self.app.get(reverse('server_run:schedule_activate', kwargs={
            'uuid': self.environment.uuid
        }), user=self.user, auto_follow=True)

        self.assertIn("Schedule is currently not active", response.text)

        scheduled = ScheduledTestScenario.objects.filter(environment=self.environment)

        self.assertEqual(scheduled.count(), 1)
        self.assertEqual(scheduled.first().active, False)

    def test_reactivate_schedule(self):
        self.app.get(reverse('server_run:server-run_create_schedule', kwargs={
            'uuid': self.environment.uuid
        }), user=self.user)

        self.app.get(reverse('server_run:schedule_activate', kwargs={
            'uuid': self.environment.uuid
        }), user=self.user, auto_follow=True)

        response = self.app.get(reverse('server_run:schedule_activate', kwargs={
            'uuid': self.environment.uuid
        }), user=self.user, auto_follow=True)

        self.assertIn("Scheduled to run", response.text)

        scheduled = ScheduledTestScenario.objects.filter(environment=self.environment)

        self.assertEqual(scheduled.count(), 1)
        self.assertEqual(scheduled.first().active, True)


class TestScenarioDetail(WebTest):

    def setUp(self):
        self.pts = PostmanTestSubFolderFactory()

    def test_scenario_detail(self):
        call = self.app.get(reverse('server_run:testscenario-detail', kwargs={
            'pk': self.pts.test_scenario.id
        }))
        self.assertIn('test subsub', call.text)


class ServerRunHiddenVarsTests(WebTest):

    def setUp(self):
        self.user, self.user2 = UserFactory.create_batch(2)
        self.test_scenario = PostmanTestFactory().test_scenario

        self.environment = EnvironmentFactory.create()

        tsu1 = TestScenarioUrlFactory(hidden=True, test_scenario=self.test_scenario, name='tsu1')
        tsu2 = TestScenarioUrlFactory(hidden=False, test_scenario=self.test_scenario, name='tsu2')
        self.server_run = ServerRunFactory.create(test_scenario=self.test_scenario, user=self.user, environment=self.environment)
        _ = EndpointFactory(test_scenario_url=tsu1, server_run=self.server_run, url='https://url1.com/', environment=self.environment)
        _ = EndpointFactory(test_scenario_url=tsu2, server_run=self.server_run, url='https://url2.com/', environment=self.environment)

        self.detail_url = reverse('server_run:server-run_detail', kwargs={'uuid': self.server_run.uuid})


    def test_detail_page_replace_hidden_vars_with_placeholders_for_other_user(self):
        response = self.app.get(self.detail_url, user=self.user2)

        self.assertNotContains(response, 'https://url1.com/')
        self.assertContains(response, 'https://url2.com/')

    def test_detail_page_replace_hidden_vars_with_placeholders_for_no_user(self):
        response = self.app.get(self.detail_url)

        self.assertNotContains(response, 'https://url1.com/')
        self.assertContains(response, 'https://url2.com/')

    def test_detail_page_hidden_vars_visible_for_same_user(self):
        response = self.app.get(self.detail_url, user=self.user)

        self.assertContains(response, 'https://url1.com/')
        self.assertContains(response, 'https://url2.com/')


class ServerRunPublicLogsTests(WebTest):

    def setUp(self):
        self.user1, self.user2 = UserFactory.create_batch(2)

        test_result_public = PostmanTestResultFactory.create(
            postman_test__name='test1',
            server_run__test_scenario__public_logs=True,
            server_run__user=self.user1,
        )
        server_run = test_result_public.server_run
        self.detail_url_public = reverse('server_run:server-run_detail', kwargs={'uuid': server_run.uuid})
        self.log_json_url_public = reverse('server_run:server-run_detail_log_json', kwargs={
            'uuid': server_run.uuid,
            'test_result_pk': test_result_public.pk,
        })
        self.log_html_url_public = reverse('server_run:server-run_detail_log', kwargs={
            'uuid': server_run.uuid,
            'test_result_pk': test_result_public.pk,
        })

        test_result_private = PostmanTestResultFactory.create(
            server_run__test_scenario__public_logs=False,
            server_run__user=self.user1,
        )
        server_run = test_result_private.server_run
        self.detail_url_private = reverse('server_run:server-run_detail', kwargs={'uuid': server_run.uuid})
        self.log_json_url_private = reverse('server_run:server-run_detail_log_json', kwargs={
            'uuid': server_run.uuid,
            'test_result_pk': test_result_private.pk,
        })
        self.log_html_url_private = reverse('server_run:server-run_detail_log', kwargs={
            'uuid': server_run.uuid,
            'test_result_pk': test_result_private.pk,
        })

    def test_show_public_logs_same_user(self):
        response = self.app.get(self.detail_url_public, user=self.user1)

        self.assertContains(response, self.log_json_url_public)
        self.assertContains(response, self.log_html_url_public)

    def test_show_public_logs_different_user(self):
        response = self.app.get(self.detail_url_public, user=self.user2)

        self.assertContains(response, self.log_json_url_public)
        self.assertContains(response, self.log_html_url_public)

    def test_show_public_logs_no_user(self):
        response = self.app.get(self.detail_url_public)

        self.assertContains(response, self.log_json_url_public)
        self.assertContains(response, self.log_html_url_public)

    def test_show_private_logs_same_user(self):
        response = self.app.get(self.detail_url_private, user=self.user1)

        self.assertContains(response, self.log_json_url_private)
        self.assertContains(response, self.log_html_url_private)

    def test_show_private_logs_different_user(self):
        response = self.app.get(self.detail_url_private, user=self.user2)

        self.assertNotContains(response, self.log_json_url_private)
        self.assertNotContains(response, self.log_html_url_private)

    def test_show_private_logs_no_user(self):
        response = self.app.get(self.detail_url_private)

        self.assertNotContains(response, self.log_json_url_private)
        self.assertNotContains(response, self.log_html_url_private)

    def test_access_public_logs_same_user(self):
        response = self.app.get(self.log_json_url_public, user=self.user1)
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.log_html_url_public, user=self.user1)
        self.assertEqual(response.status_code, 200)

    def test_access_public_logs_different_user(self):
        response = self.app.get(self.log_json_url_public, user=self.user2)
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.log_html_url_public, user=self.user2)
        self.assertEqual(response.status_code, 200)

    def test_access_public_logs_no_user(self):
        response = self.app.get(self.log_json_url_public)
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.log_html_url_public)
        self.assertEqual(response.status_code, 200)

    def test_access_private_logs_same_user(self):
        response = self.app.get(self.log_json_url_private, user=self.user1)
        self.assertEqual(response.status_code, 200)

        response = self.app.get(self.log_html_url_private, user=self.user1)
        self.assertEqual(response.status_code, 200)

    def test_access_private_logs_different_user(self):
        response = self.app.get(self.log_json_url_private, user=self.user2, status=[403])
        self.assertEqual(response.status_code, 403)

        response = self.app.get(self.log_html_url_private, user=self.user2, status=[403])
        self.assertEqual(response.status_code, 403)

    def test_access_private_logs_no_user(self):
        response = self.app.get(self.log_json_url_private, status=[403])
        self.assertEqual(response.status_code, 403)

        response = self.app.get(self.log_html_url_private, status=[403])
        self.assertEqual(response.status_code, 403)


class TestServerRunList(WebTest):

    def setUp(self):
        self.test_scenario = TestScenarioFactory.create()

        self.tsf = TestScenarioUrlFactory(name='url', test_scenario=self.test_scenario)
        self.pt = PostmanTestFactory(test_scenario=self.test_scenario)
        self.user = UserFactory(username='testuser1')

        self.environment = EnvironmentFactory.create(
            name='testenv', test_scenario=self.test_scenario, user=self.user
        )
        self.server_run = ServerRunFactory(
            test_scenario=self.test_scenario,
            environment=self.environment,
            user=self.user
        )
        self.postman_result = PostmanTestResultFactory(server_run=self.server_run)

    def test_server_run_list(self):
        response = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': self.test_scenario.uuid,
            'env_uuid': self.environment.uuid
        }), auto_follow=True, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertIn('testenv', response.text)

    def test_server_run_list_without_json_file(self):
        self.postman_result.log_json = None
        self.postman_result.save()
        response = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': self.test_scenario.uuid,
            'env_uuid': self.environment.uuid
        }), auto_follow=True, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertIn('testenv', response.text)

    def test_server_run_list_without_html_file(self):
        self.postman_result.log = None
        self.postman_result.save()
        response = self.app.get(reverse('server_run:server-run_list', kwargs={
            'scenario_uuid': self.test_scenario.uuid,
            'env_uuid': self.environment.uuid
        }), auto_follow=True, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertIn('testenv', response.text)
