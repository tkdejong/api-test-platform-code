import os
import json

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from vng.design_rules.tasks.dr_20200709 import run_20200709_api_56

from ...factories import DesignRuleResultFactory, DesignRuleSessionFactory
from ....choices import DesignRuleChoices
from ....models import DesignRuleResult


class Api56Tests(TestCase):
    def test_design_rule_already_exists(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")
        pre_result = DesignRuleResultFactory(design_rule=session, rule_type=DesignRuleChoices.api_56_20200709)

        result = run_20200709_api_56(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertEqual(pre_result.pk, result.pk)

    def test_no_json_provided(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        result = run_20200709_api_56(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("The API did not give a valid JSON output.")])

    def test_successful_version(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_20200709_api_56(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertEqual(result.errors, None)

    def test_no_version_found(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "no_version.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_20200709_api_56(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("There is no openapi version found.")])

    def test_version_not_semver(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "invalid_version.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        result = run_20200709_api_56(session)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("The given version does not resamble a SemVer version.")])
