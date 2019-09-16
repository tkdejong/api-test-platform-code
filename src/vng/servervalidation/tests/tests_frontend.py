import factory
import json

from django_webtest import WebTest
from django.urls import reverse

from vng.testsession.tests.factories import UserFactory
from vng.servervalidation.models import ServerRun, PostmanTest, PostmanTestResult, User

from .factories import (
    TestScenarioFactory, ServerRunFactory, TestScenarioUrlFactory, PostmanTestFactory,
    UserFactory, PostmanTestSubFolderFactory, EndpointFactory, PostmanTestResultFactory
)
from ...utils import choices, forms


class TestMultipleEndpoint(WebTest):

    def setUp(self):
        self.user = UserFactory()
        self.ts = TestScenarioFactory()
        self.ts.authorization = choices.AuthenticationChoices.no_auth
        self.ts.save()
        TestScenarioUrlFactory(test_scenario=self.ts)
        TestScenarioUrlFactory(test_scenario=self.ts)

    def test_run_collection(self):
        call = self.app.get(reverse('server_run:server-run_create_item'), user=self.user)
        form = call.forms[1]
        form['test_scenario'] = self.ts.pk
        res = form.submit().follow()

        form = res.forms[1]
        for name, _ in form.field_order:
            if name is not None and 'test_scenario' in name:
                print(name)
                n = name
        form[n] = 'https://ref.tst.vng.cloud/drc/api/v1/'
        form['url'] = 'https://ref.tst.vng.cloud/drc/api/v1/'
        form.submit()


class TestCreation(WebTest):

    def setUp(self):
        self.tsf = TestScenarioUrlFactory()
        self.pt = PostmanTestFactory()
        self.user = UserFactory()
        self.server = ServerRunFactory()

        self.test_scenario = self.tsf.test_scenario
        self.server.test_scenario = self.test_scenario
        self.pt.test_scenario = self.test_scenario
        self.server.user = self.user

        self.pt.save()
        self.server.save()

    def test_creation_error_list(self):
        call = self.app.get(reverse('server_run:server-run_list'), user='test')
        self.assertNotIn('Starting', call.text)

        call = self.app.get(reverse('server_run:server-run_create_item'), user='test')
        form = call.forms[1]
        form['test_scenario'].force_value('9')
        form.submit()
        call = self.app.get(reverse('server_run:server-run_list'), user='test')
        self.assertNotIn('Starting', call.text)

    def test_scenarios(self):
        call = self.app.get(reverse('server_run:server-run_create_item'), user=self.user)
        form = call.forms[1]
        form['test_scenario'] = self.tsf.test_scenario.pk

        res = form.submit().follow()
        form = res.forms[1]
        form['url'] = 'https://ref.tst.vng.cloud/drc/api/v1/'
        form['Client ID'] = 'client id'
        form['Secret'] = 'secret'
        form.submit()
        call = self.app.get(reverse('server_run:server-run_list'), user=self.user)
        self.assertIn(self.user.username, call.text)
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
        server = ServerRun.objects.filter(user=self.user).order_by('-started')[0]
        url = reverse('server_run:server-run_detail', kwargs={
            'uuid': server.uuid
        })
        call = self.app.get(url, user=self.user)
        self.assertIn(str(server.pk), call.text)


class TestList(WebTest):

    def setUp(self):
        TestScenarioFactory()
        ServerRunFactory()

    def test_list(self):
        call = self.app.get(reverse('server_run:server-run_list'), user='test')
        assert 'no session' not in str(call.body)


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
        self.server = ServerRunFactory()
        self.test_scenario = TestScenarioUrlFactory().test_scenario
        PostmanTestFactory(test_scenario=self.test_scenario)
        self.server_s = ServerRunFactory(test_scenario=self.test_scenario, scheduled=True)
        self.user = self.server_s.user

    def test_access(self):
        call = self.app.get(reverse('server_run:server-run_detail', kwargs={
            'uuid': self.server.uuid
        }))
        self.assertIn(str(self.server.id), call.text)

    def test_trigger(self):
        prev = len(PostmanTestResult.objects.all())
        self.app.get(
            reverse('server_run:server-run_trigger', kwargs={
                'server_id': self.server_s.id
            }), user=self.server_s.user
        )
        self.assertEqual(prev, len(PostmanTestResult.objects.all()) - 1)

    def test_badge(self):
        call = self.app.get(reverse('server_run:server-run_create_item'), user=self.user)
        form = call.forms[1]
        form['test_scenario'] = self.server_s.test_scenario.pk
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
        call = self.app.get(reverse('server_run:server-run_list'), user=self.user)
        ptr = PostmanTestResult.objects.all()[0]
        self.assertIn(str(ptr.get_assertions_details()[0]), call.text)

    def test_session_number_no_user(self):
        # simply check that with no user it raises no errors
        call = self.app.get(reverse('server_run:server-run_list'), status=[200, 302])

    def test_session_number_user(self):
        call = self.app.get(reverse('server_run:server-run_list'), user=self.user)
        self.assertIn(str(ServerRun.objects.filter(user=self.user, scheduled=True).count()), call.text)

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

        tsu1 = TestScenarioUrlFactory(hidden=True, test_scenario=self.test_scenario, name='tsu1')
        tsu2 = TestScenarioUrlFactory(hidden=False, test_scenario=self.test_scenario, name='tsu2')
        self.server_run = ServerRunFactory.create(test_scenario=self.test_scenario, user=self.user)
        _ = EndpointFactory(test_scenario_url=tsu1, server_run=self.server_run, url='https://url1.com/')
        _ = EndpointFactory(test_scenario_url=tsu2, server_run=self.server_run, url='https://url2.com/')

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
        with open(test_result_public.log_json.path, 'w') as f:
            json.dump(
                {
                    'run': {
                        'executions': [{'request': {'url': 'test'}}],
                        'timings': {'started': '100', 'stopped': '200'}
                    }
                },
                f
            )

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
        with open(test_result_private.log_json.path, 'w') as f:
            json.dump(
                {
                    'run': {
                        'executions': [{'request': {'url': 'test'}}],
                        'timings': {'started': '100', 'stopped': '200'}
                    }
                },
                f
            )

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
