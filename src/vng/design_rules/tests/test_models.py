from decimal import Decimal
import os
import json

from django.test import TestCase

import requests_mock

from .factories import DesignRuleSessionFactory, DesignRuleTestSuiteFactory, DesignRuleResultFactory, DesignRuleTestVersionFactory, DesignRuleTestOptionFactory
from ..choices import DesignRuleChoices
from ..models import DesignRuleSession, DesignRuleResult


class DesignRuleTestSuiteTests(TestCase):
    def setUp(self):
        self.test_version = DesignRuleTestVersionFactory()
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_03_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_09_20200117)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_16_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_20_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_48_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_51_20200709)

    def test_start_session(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "tasks", "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1', json=json.loads(json_file.read()))
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-session/", status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-testsuite/", status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/", status_code=404)
            test_suite.start_session(self.test_version)
        self.assertEqual(DesignRuleSession.objects.count(), 1)
        self.assertEqual(DesignRuleResult.objects.count(), 6)

    def test_successful(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "tasks", "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1/openapi.json', json=json.loads(json_file.read()), headers={"Access-Control-Allow-Origin": "http://foo.example"})
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-session/", status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-testsuite/", status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/", status_code=404)
            test_suite.start_session(self.test_version)
        self.assertTrue(test_suite.successful())
        self.assertEqual(test_suite.percentage_score(), Decimal("100.00"))

    def test_successful_no_sessions(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        self.assertFalse(test_suite.successful())

    def test_percentage_score(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "tasks", "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1/openapi.json', json=json.loads(json_file.read()), headers={"Access-Control-Allow-Origin": "http://foo.example"})
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-session/", status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-testsuite/", status_code=404)
                mock.post("http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/", status_code=404)
            test_suite.start_session(self.test_version)
        self.assertEqual(test_suite.percentage_score(), Decimal("100.00"))

    def test_percentage_score_no_sessions(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        self.assertEqual(test_suite.percentage_score(), Decimal("0.00"))


class DesignRuleSessionTests(TestCase):
    def test_design_rule_session_no_resutls(self):
        session = DesignRuleSessionFactory()
        self.assertFalse(session.successful())

    def test_design_rule_session_all_success(self):
        session = DesignRuleSessionFactory()
        DesignRuleResultFactory(success=True, design_rule=session)
        DesignRuleResultFactory(success=True, design_rule=session)
        self.assertTrue(session.successful())

    def test_design_rule_session_all_not_success(self):
        session = DesignRuleSessionFactory()
        DesignRuleResultFactory(success=False, design_rule=session)
        self.assertFalse(session.successful())
