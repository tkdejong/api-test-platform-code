import os
import json

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from vng.design_rules.tasks.api_09 import run_api_09_test_rules

from ..factories import DesignRuleResultFactory, DesignRuleSessionFactory
from ...choices import DesignRuleChoices
from ...models import DesignRuleResult


class Api09Tests(TestCase):
    def test_design_rule_already_exists(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")
        pre_result = DesignRuleResultFactory(design_rule=session, rule_type=DesignRuleChoices.api_09)

        result = run_api_09_test_rules(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertEqual(pre_result.pk, result.pk)

    def test_no_json_provided(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        result = run_api_09_test_rules(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, "The API did not give a valid JSON output.")

    def test_successful_no_fields(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "files", "no_version.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_api_09_test_rules(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertEqual(result.errors, "")

    def test_successful_with_fields(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "files", "good.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_api_09_test_rules(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertEqual(result.errors, "")

    def test_successful_with_fields_no_enum(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "files", "no_fields_enum.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_api_09_test_rules(session)
        errors = _("there are no field options found for path: {}, method: {}").format("/auth/login", "post")
        errors += "\n"
        errors += _("there are no field options found for path: {}, method: {}").format("/designrule-testsuite/{uuid}", "get")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, errors)

    def test_successful_with_fields_no_schema(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "files", "no_fields_schema.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_api_09_test_rules(session)
        errors = _("there is no schema for the field parameter found for path: {}, method: {}").format("/auth/login", "post")
        errors += "\n"
        errors += _("there is no schema for the field parameter found for path: {}, method: {}").format("/designrule-testsuite/{uuid}", "get")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, errors)
