from decimal import Decimal
import os
import json

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

import requests_mock
from vng.design_rules.choices import DesignRuleChoices
from vng.design_rules.tasks.base import run_tests

from ..factories import DesignRuleSessionFactory, DesignRuleTestOptionFactory, DesignRuleTestVersionFactory
from ...models import DesignRuleResult


class BaseAPITests(TestCase):
    def setUp(self):
        self.test_version = DesignRuleTestVersionFactory()
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_03_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_09_20200117)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_16_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_20_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_48_20200709)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_51_20200117)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_51_20200709)

    def test_yaml_response(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "openapi.yaml")) as html_file:
                mock.get('https://maykinmedia.nl/openapi.json', status_code=404)
                mock.get('https://maykinmedia.nl/openapi.yaml', text=html_file.read())
                mock.get('https://maykinmedia.nl/designrule-session/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-session/%7Bid%7D/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-session/%7Bid%7D/shield/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-testsuite/', status_code=404)
                mock.post('https://maykinmedia.nl/designrule-testsuite/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-testsuite/%7Bid%7D/', status_code=404)
                mock.post('https://maykinmedia.nl/designrule-testsuite/%7Bid%7D/start_session/', status_code=404)
            run_tests(session, "https://maykinmedia.nl")
        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("57.14"))

    def test_specification_url(self):
        spec_url = "http://localhost:8000/docs/openapi.json"
        session = DesignRuleSessionFactory(test_suite__api_endpoint="http://localhost:8000/api/v1", test_suite__specification_url=spec_url, test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as html_file:
                mock.get('http://localhost:8000/api/v1/openapi.json', status_code=404)
                mock.get('http://localhost:8000/api/v1/openapi.yaml', status_code=404)
                mock.get(spec_url, text=html_file.read(), headers={"Access-Control-Allow-Origin": "http://foo.example"})
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/', status_code=404)
            run_tests(session, "http://localhost:8000/api/v1", spec_url)
        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("87.71"))

    def test_unnecessary_specification_url(self):
        spec_url = "http://localhost:8000/docs/openapi.json"
        session = DesignRuleSessionFactory(test_suite__api_endpoint="http://localhost:8000/api/v1", test_suite__specification_url=spec_url, test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as html_file:
                # The OAS file is also served on the expected path,
                # so api_51_20200709 should succeed and give us full points
                mock.get('http://localhost:8000/api/v1/openapi.json', text=html_file.read(), headers={"Access-Control-Allow-Origin": "http://foo.example"})
                mock.get('http://localhost:8000/api/v1/openapi.yaml', status_code=404)
                mock.get(spec_url, text=html_file.read(), headers={"Access-Control-Allow-Origin": "http://foo.example"})
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/', status_code=404)
            run_tests(session, "http://localhost:8000/api/v1", spec_url)
        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertTrue(session.successful())
        self.assertEqual(session.percentage_score, Decimal("100"))

    def test_no_json_or_yaml_response(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "website.html")) as html_file:
                mock.get('https://maykinmedia.nl', text=html_file.read())
            run_tests(session, "https://maykinmedia.nl")
        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("0"))

    def test_all_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="http://localhost:8000/api/v1", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1/openapi.json', json=json.loads(json_file.read()), headers={"Access-Control-Allow-Origin": "http://foo.example"})
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/', status_code=404)
            run_tests(session, "http://localhost:8000/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertTrue(session.successful())
        self.assertEqual(session.percentage_score, Decimal("100"))

    def test_old_api_loading(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="http://localhost:8000/api/v1", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1/openapi.json', status_code=404)
                mock.get('http://localhost:8000/api/v1/openapi.yaml', status_code=404)
                mock.get('http://localhost:8000/api/v1', json=json.loads(json_file.read()))
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/', status_code=404)
            run_tests(session, "http://localhost:8000/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("85.71"))

    def test_return_cors_headers(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="http://localhost:8000/api/v1", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1/openapi.json', json=json.loads(json_file.read()), headers={"Access-Control-Allow-Origin": "http://foo.example"})
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/', status_code=404)
            run_tests(session, "http://localhost:8000/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertTrue(session.successful())
        self.assertEqual(session.percentage_score, Decimal("100"))

    def test_return_cors_headers_fail(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="http://localhost:8000/api/v1", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1/openapi.json', json=json.loads(json_file.read()), headers={"Access-Control-Allow-Origin": "http://localhost:8000/"})
                mock.get('http://localhost:8000/api/v1/designrule-session/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/', status_code=404)
                mock.get('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post('http://localhost:8000/api/v1/designrule-testsuite/%7Buuid%7D/start_session/', status_code=404)
            run_tests(session, "http://localhost:8000/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("85.71"))

    def test_some_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', json=json.loads(json_file.read()))
                mock.get('https://maykinmedia.nl/designrule-session/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-session/%7Buuid%7D/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-session/shield/%7Buuid%7D/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-testsuite/', status_code=404)
                mock.post('https://maykinmedia.nl/designrule-testsuite/', status_code=404)
                mock.get('https://maykinmedia.nl/designrule-testsuite/%7Buuid%7D/', status_code=404)
                mock.post('https://maykinmedia.nl/designrule-testsuite/%7Buuid%7D/start_session/', status_code=404)
            run_tests(session, "https://maykinmedia.nl")

        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("57.14"))

    def test_none_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "wrong.json")) as json_file:
                mock.get('https://maykinmedia.nl/openapi.json', json=json.loads(json_file.read()))
                mock.get('https://maykinmedia.nl/designrule-session/', status_code=200, json="{}")
                mock.get('https://maykinmedia.nl/designrule-session/%7Bid%7D/', status_code=200, json="{}")
                mock.get('https://maykinmedia.nl/designrule-session/%7Bid%7D/shield/', status_code=200, json="{}")
                mock.get('https://maykinmedia.nl/designrule-testsuite/', status_code=200, json="{}")
                mock.post('https://maykinmedia.nl/designrule-testsuite/', status_code=200, json="{}")
                mock.get('https://maykinmedia.nl/designrule-testsuite/%7Bid%7D/', status_code=200, json="{}")
                mock.post('https://maykinmedia.nl/designrule-testsuite/%7Bid%7D/start_session/', status_code=200, json="{}")
            run_tests(session, "https://maykinmedia.nl")

        self.assertEqual(DesignRuleResult.objects.count(), 7)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("0"))
