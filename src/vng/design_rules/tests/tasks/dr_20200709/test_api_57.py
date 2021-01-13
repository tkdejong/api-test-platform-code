import os
import json

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

import requests
import requests_mock

from vng.design_rules.tasks.dr_20200709 import run_20200709_api_57

from ...factories import DesignRuleResultFactory, DesignRuleSessionFactory
from ....choices import DesignRuleChoices
from ....models import DesignRuleResult


class Api57Tests(TestCase):
    def test_design_rule_already_exists(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")
        pre_result = DesignRuleResultFactory(design_rule=session, rule_type=DesignRuleChoices.api_57_20200709)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read())
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_57(session, response=response)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertEqual(pre_result.pk, result.pk)

    def test_no_version_heeader_provided(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read())
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_57(session, response=response)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("The headers is missing. Make sure that the 'API-Version' is given.")])

    def test_version_heeader_provided(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read(), headers={"API-Version": "1.1.1"})
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_57(session, response=response)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertIsNone(result.errors)

    def test_version_heeader_provided_lowercase(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read(), headers={"api-version": "1.1.1"})
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_57(session, response=response)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertIsNone(result.errors)

    def test_version_heeader_provided_uppercase(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read(), headers={"API-VERSION": "1.1.1"})
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_57(session, response=response)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertTrue(result.success)
        self.assertIsNone(result.errors)

    def test_version_heeader_provided_with_prefix(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read(), headers={"X-API-VERSION": "1.1.1"})
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_57(session, response=response)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("The headers is missing. Make sure that the 'API-Version' is given.")])
