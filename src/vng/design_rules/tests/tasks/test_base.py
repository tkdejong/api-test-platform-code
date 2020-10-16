from decimal import Decimal
import os
import json
from unittest.case import expectedFailure

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

import requests_mock
from vng.design_rules.tasks.base import run_tests

from ..factories import DesignRuleSessionFactory
from ...models import DesignRuleResult


class BaseAPITests(TestCase):
    def test_no_json_response(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "website.html")) as html_file:
                mock.get('https://maykinmedia.nl/', text=html_file.read())
            result = run_tests(session, "https://maykinmedia.nl/")
        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("0"))

    def test_all_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('http://localhost:8000/api/v1', json=json.loads(json_file.read()))
            result = run_tests(session, "http://localhost:8000/api/v1")

        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertTrue(session.successful())
        self.assertEqual(session.percentage_score, Decimal("100"))

    def test_some_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "good.json")) as json_file:
                mock.get('https://maykinmedia.nl/', json=json.loads(json_file.read()))
            result = run_tests(session, "https://maykinmedia.nl/")

        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("66.67"))

    @expectedFailure
    def test_none_success(self):
        session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/")

        with requests_mock.Mocker() as mock:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, "files", "wrong.json")) as json_file:
                mock.get('https://maykinmedia.nl/', json=json.loads(json_file.read()))
            result = run_tests(session, "https://maykinmedia.nl/")

        self.assertEqual(DesignRuleResult.objects.count(), 6)
        session.refresh_from_db()
        self.assertFalse(session.successful())
        self.assertEqual(session.percentage_score, Decimal("0"))
