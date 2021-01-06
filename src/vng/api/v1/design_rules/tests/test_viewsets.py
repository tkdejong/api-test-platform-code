from django.urls import reverse

from django_webtest import WebTest
from vng.design_rules.choices import DesignRuleChoices

from vng.utils.factories import UserFactory
from vng.api_authentication.tests.factories import CustomTokenFactory
from vng.design_rules.choices import DesignRuleChoices
from vng.design_rules.tests.factories import DesignRuleSessionFactory, DesignRuleTestOptionFactory, DesignRuleTestSuiteFactory, DesignRuleTestVersionFactory, DesignRuleResultFactory


class DesignRuleTestSuiteViewSetTests(WebTest):
    def test_view_is_protected(self):
        test_suite = DesignRuleTestSuiteFactory()
        url = reverse("api_v1_design_rules:test_suite-start-session", kwargs={"uuid": test_suite.uuid})
        self.app.post(url, status=401)

    def test_start_session(self):
        test_version = DesignRuleTestVersionFactory()
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_03_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_09_20200117)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_16_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_20_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_48_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_51_20200709)

        token = CustomTokenFactory()
        test_suite = DesignRuleTestSuiteFactory()
        url = reverse("api_v1_design_rules:test_suite-start-session", kwargs={"uuid": test_suite.uuid})
        extra_environ = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        response = self.app.post(url, params={"test_version": test_version.id}, extra_environ=extra_environ)
        self.assertEqual(response.status_code, 201)

    def test_start_session_design_rule_test_version_does_not_exist(self):
        token = CustomTokenFactory()
        test_suite = DesignRuleTestSuiteFactory()
        url = reverse("api_v1_design_rules:test_suite-start-session", kwargs={"uuid": test_suite.uuid})
        extra_environ = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        response = self.app.post(url, params={"test_version": 1}, extra_environ=extra_environ, status=400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"test_version": ['Invalid pk "1" - object does not exist.']})

    def test_start_session_test_version_not_active(self):
        test_version = DesignRuleTestVersionFactory(is_active=False)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_03_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_09_20200117)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_16_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_20_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_48_20200709)
        DesignRuleTestOptionFactory(test_version=test_version, rule_type=DesignRuleChoices.api_51_20200709)

        token = CustomTokenFactory()
        test_suite = DesignRuleTestSuiteFactory()
        url = reverse("api_v1_design_rules:test_suite-start-session", kwargs={"uuid": test_suite.uuid})
        extra_environ = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        response = self.app.post(url, params={"test_version": test_version.id}, extra_environ=extra_environ, status=400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"test_version": ['The test version "{}" is inactive.'.format(str(test_version))]})


class DesignRuleSessionViewSetTests(WebTest):
    def test_shield(self):
        session = DesignRuleSessionFactory()
        url = reverse("api_v1_design_rules:design_rule-shield", kwargs={"uuid": session.uuid})
        self.app.get(url)

    def test_shield_100(self):
        session = DesignRuleSessionFactory(percentage_score=100)
        url = reverse("api_v1_design_rules:design_rule-shield", kwargs={"uuid": session.uuid})
        response = self.app.get(url)

    def test_retreive_session(self):
        token = CustomTokenFactory()
        session = DesignRuleSessionFactory(percentage_score=100)
        DesignRuleResultFactory(success=True, design_rule=session, rule_type=DesignRuleChoices.api_03_20200709)

        extra_environ = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        url = reverse("api_v1_design_rules:session-detail", kwargs={"uuid": session.uuid})
        response = self.app.get(url, extra_environ=extra_environ)
        self.assertEqual(response.json['results'], [{
            'errors': '', 'rule_type': 'api_03', 'success': True,
            "url": "https://docs.geostandaarden.nl/api/API-Designrules/#api-03-only-apply-default-http-operations",
            "description": "A RESTful API is an application programming interface that supports the default HTTP operations GET, PUT, POST, PATCH and DELETE."
        }])
