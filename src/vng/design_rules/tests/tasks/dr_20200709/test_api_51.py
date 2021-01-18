import os
import json

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

import requests
import requests_mock

from vng.design_rules.tasks.dr_20200709 import run_20200709_api_51

from ...factories import DesignRuleResultFactory, DesignRuleSessionFactory
from ....choices import DesignRuleChoices
from ....models import DesignRuleResult


class Api51Tests(TestCase):
    def test_design_rule_already_exists(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")
        pre_result = DesignRuleResultFactory(design_rule=session, rule_type=DesignRuleChoices.api_51_20200709)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read())
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_51(session, response=response, is_json=True)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertEqual(pre_result.pk, result.pk)

    def test_no_json_provided(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read())
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_51(session, response=response, is_json=True)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("The API did not give a valid JSON output.")])

    def test_no_cors_headers(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "first_path_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read())
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_51(session, response=response, is_json=True)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, [_("There are no CORS headers set. Please make sure that CORS headers are set.")])

    def test_base_as_first_path(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "first_path_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read(), headers={"Access-Control-Allow-Origin": "http://foo.example"})
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_51(session, response=response, is_json=True)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, None)
        self.assertEqual(result.warnings, [_("The OAS file was not found at /openapi.json or at /openapi.yaml")])

    def test_base_in_server(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "server_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', text=json_file.read(), headers={"Access-Control-Allow-Origin": "http://foo.example"})
            response = requests.get("https://maykinmedia.nl/openapi.json")

        result = run_20200709_api_51(session, response=response, is_json=True)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.warnings, [_("The OAS file was not found at /openapi.json or at /openapi.yaml")])

    def test_is_not_json_parsed(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "server_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "openapi.yaml")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.yaml', text=json_file.read(), headers={"Access-Control-Allow-Origin": "http://foo.example"})
            response = requests.get("https://maykinmedia.nl/openapi.yaml")

        result = run_20200709_api_51(session, response=response, correct_location=True, is_json=False)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.warnings, [_("The API did not give a valid JSON output. It most likely was YAML")])

    def test_is_not_correct_location(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "..", "files", "server_endpoint.json")) as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json.loads(json_file.read()))

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "..", "files", "openapi.yaml")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.yaml', text=json_file.read(), headers={"Access-Control-Allow-Origin": "http://foo.example"})
            response = requests.get("https://maykinmedia.nl/openapi.yaml")

        result = run_20200709_api_51(session, response=response, correct_location=False, is_json=True)
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.warnings, [_("The OAS file was not found at /openapi.json or at /openapi.yaml")])
