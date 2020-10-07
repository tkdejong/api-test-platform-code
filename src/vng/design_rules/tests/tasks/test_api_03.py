from django.test import TestCase

from vng.design_rules.tasks.api_20 import run_api_20_test_rules

from ..factories import DesignRuleSessionFactory
from ...models import DesignRuleResult


class Api20Tests(TestCase):
    def test_no_version(self):
        with open() as json_file:
            session = DesignRuleSessionFactory(test_suite__api_endpoint="https://maykinmedia.nl/", json_result=json_file.read())

        result = run_api_20_test_rules(session, "https://maykinmedia.nl/")
        self.assertEqual(DesignRuleResult.objects.count(), 1)
        self.assertFalse(result.success)
        self.assertEqual(result.errors, "The api endpoint does not contain a 'v*' in the url")
