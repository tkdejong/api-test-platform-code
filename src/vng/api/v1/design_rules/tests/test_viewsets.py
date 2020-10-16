from django.urls import reverse

from django_webtest import WebTest

from vng.utils.factories import UserFactory
from vng.api_authentication.tests.factories import CustomTokenFactory
from vng.design_rules.tests.factories import DesignRuleSessionFactory, DesignRuleTestSuiteFactory


class DesignRuleTestSuiteViewSetTests(WebTest):
    def test_view_is_protected(self):
        test_suite = DesignRuleTestSuiteFactory()
        url = reverse("api_v1_design_rules:test_suite-start-session", kwargs={"uuid": test_suite.uuid})
        self.app.post(url, status=401)

    def test_start_session(self):
        token = CustomTokenFactory()
        test_suite = DesignRuleTestSuiteFactory()
        url = reverse("api_v1_design_rules:test_suite-start-session", kwargs={"uuid": test_suite.uuid})
        extra_environ = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        response = self.app.post(url, extra_environ=extra_environ)
        self.assertEquals(response.status_code, 201)


class DesignRuleSessionViewSetTests(WebTest):
    def test_shield(self):
        session = DesignRuleSessionFactory()
        url = reverse("api_v1_design_rules:design_rule-shield", kwargs={"uuid": session.uuid})
        response = self.app.get(url)

    def test_shield_100(self):
        session = DesignRuleSessionFactory(percentage_score=100)
        url = reverse("api_v1_design_rules:design_rule-shield", kwargs={"uuid": session.uuid})
        response = self.app.get(url)
