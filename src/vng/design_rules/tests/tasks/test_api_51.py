import os
import json

from django.test import TestCase

from vng.design_rules.tasks.api_51 import run_api_51_test_rules

from ..factories import DesignRuleResultFactory, DesignRuleSessionFactory
from ...choices import DesignRuleChoices
from ...models import DesignRuleResult


class Api51Tests(TestCase):
    def test_design_rule_already_exists(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")
        pre_result = DesignRuleResultFactory(design_rule=session, rule_type=DesignRuleChoices.api_51)

        result = run_api_51_test_rules(session, "https://maykinmedia.nl/")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertEqual(pre_result.pk, result.pk)

    def test_no_json_provided(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        result = run_api_51_test_rules(session, "https://maykinmedia.nl/")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, "The API did not give a valid JSON output.")

    def test_base_not_found(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "files", "first_path_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_api_51_test_rules(session, "https://maykinmedia.nl/")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, "The endpoint does not seems to be the root endpoint")

    def test_base_as_first_path(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "files", "first_path_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_api_51_test_rules(session, "https://maykinmedia.nl/api/v1")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertEqual(result.errors, "")

    def test_base_in_server(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "files", "server_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_api_51_test_rules(session, "https://maykinmedia.nl/api/v1")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertEqual(result.errors, "")
