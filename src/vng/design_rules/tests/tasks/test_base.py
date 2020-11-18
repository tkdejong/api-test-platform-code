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
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_03)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_09)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_16)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_20)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_48)
        DesignRuleTestOptionFactory(test_version=self.test_version, rule_type=DesignRuleChoices.api_51)

    def test_yaml_response(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "openapi.yaml")) as html_file:
                mock.get('https://maykinmedia.nl/', text=html_file.read())
            run_tests(session, "https://maykinmedia.nl/")
        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("66.67"))

    def test_no_json_or_yaml_response(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "website.html")) as html_file:
                mock.get('https://maykinmedia.nl/', text=html_file.read())
            run_tests(session, "https://maykinmedia.nl/")
        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("0"))

    def test_all_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1', json=json.loads(json_file.read()))
            run_tests(session, "http://localhost:8000/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertTrue(session.successful())
        self.assertEqual(session.percentage_score, Decimal("100"))

    def test_some_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/', json=json.loads(json_file.read()))
            run_tests(session, "https://maykinmedia.nl/")

        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("66.67"))

    def test_none_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", test_version=self.test_version)

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "wrong.json")) as json_file:
                mock.get('https://maykinmedia.nl/', json=json.loads(json_file.read()))
            run_tests(session, "https://maykinmedia.nl/")

        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("0"))
