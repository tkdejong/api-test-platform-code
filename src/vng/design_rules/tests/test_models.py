from decimal import Decimal
import os
import json

from django.test import TestCase

import requests_mock

from .factories import DesignRuleTestSuiteFactory
from ..models import DesignRuleSession, DesignRuleResult


class DesignRuleTestSuiteTests(TestCase):
    def test_start_session(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "tasks", "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1', json=json.loads(json_file.read()))
            test_suite.start_session()
        self.assertEqual(DesignRuleSession.objects.count(), 1)
        self.assertEqual(DesignRuleResult.objects.count(), 6)

    def test_successful(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "tasks", "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1', json=json.loads(json_file.read()))
            test_suite.start_session()
        self.assertTrue(test_suite.successful())

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
                mock.get('http://localhost:8000/api/v1', json=json.loads(json_file.read()))
            test_suite.start_session()
        self.assertEqual(test_suite.percentage_score(), Decimal("100.00"))

    def test_percentage_score_no_sessions(self):
        test_suite = DesignRuleTestSuiteFactory(api_endpoint="http://localhost:8000/api/v1")
        self.assertEqual(DesignRuleSession.objects.count(), 0)
        self.assertEqual(DesignRuleResult.objects.count(), 0)

        self.assertEqual(test_suite.percentage_score(), Decimal("0.00"))


class DesignRuleSessionTests(TestCase):
    # TODO: Write the tests
    pass
