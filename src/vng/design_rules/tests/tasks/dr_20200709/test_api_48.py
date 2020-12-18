import os
import json

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

import requests_mock

from vng.design_rules.tasks.dr_20200709 import run_20200709_api_48

from ...factories import DesignRuleResultFactory, DesignRuleSessionFactory
from ....choices import DesignRuleChoices
from ....models import DesignRuleResult


class Api48Tests(TestCase):
    def test_design_rule_already_exists(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/api/v1")
        pre_result = DesignRuleResultFactory(design_rule=session, rule_type=DesignRuleChoices.api_48_20200709)

        result = run_20200709_api_48(session, "https://maykinmedia.nl/api/v1")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertEqual(pre_result.pk, result.pk)

    def test_no_json_provided(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/api/v1")

        result = run_20200709_api_48(session, "https://maykinmedia.nl/api/v1")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("The API did not give a valid JSON output.")])

    def test_no_trailing_slashes(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/api/v1", json_result=json.loads(json_file.read()))

        with requests_mock.Mocker() as mock:
            mock.get('https://maykinmedia.nl/api/v1/designrule-session/', status_code=404)
            mock.get('https://maykinmedia.nl/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
            mock.get('https://maykinmedia.nl/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
            mock.get('https://maykinmedia.nl/api/v1/designrule-testsuite/', status_code=404)
            mock.get('https://maykinmedia.nl/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
            mock.post("https://maykinmedia.nl/api/v1/designrule-session/", status_code=404)
            mock.post("https://maykinmedia.nl/api/v1/designrule-testsuite/", status_code=404)
            mock.post("https://maykinmedia.nl/api/v1/designrule-testsuite/%7Buuid%7D/start_session/", status_code=404)

            result = run_20200709_api_48(session, "https://maykinmedia.nl/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertEqual(result.errors, None)

    def test_no_trailing_slashes_no_404_result(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/api/v1", json_result=json.loads(json_file.read()))

        with requests_mock.Mocker() as mock:
            mock.get('https://maykinmedia.nl/api/v1/designrule-session/', status_code=200, text="Logging out")
            mock.get('https://maykinmedia.nl/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404, text="Logging out")
            mock.get('https://maykinmedia.nl/api/v1/designrule-session/%7Buuid%7D/', status_code=404, text="Logging out")
            mock.get('https://maykinmedia.nl/api/v1/designrule-testsuite/', status_code=404, text="Logging out")
            mock.get('https://maykinmedia.nl/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404, text="Logging out")
            mock.post("https://maykinmedia.nl/api/v1/designrule-testsuite/", status_code=404, text="Logging out")
            mock.post("https://maykinmedia.nl/api/v1/designrule-testsuite/%7Buuid%7D/start_session/", status_code=404, text="Logging out")

            result = run_20200709_api_48(session, "https://maykinmedia.nl/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [
            'Path: /designrule-session/ with a slash at the end did not result in a 404. it resulted in a 200'
        ])

    def test_with_trailing_slashes(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "with_trailing_slashes.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/api/v1", json_result=json.loads(json_file.read()))

        result = run_20200709_api_48(session, "https://maykinmedia.nl/api/v1")
        errors = [
            _("Path: {} ends with a slash").format("/designrule-session/"),
            _("Path: {} ends with a slash").format("/designrule-session/{id}/"),
        ]
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, errors)

    def test_with_no_paths(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "no_paths.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/api/v1", json_result=json.loads(json_file.read()))

        result = run_20200709_api_48(session, "https://maykinmedia.nl/api/v1")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("There are no paths found")])
