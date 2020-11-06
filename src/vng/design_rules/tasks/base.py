from json import JSONDecodeError
from decimal import Decimal

import requests
from celery.utils.log import get_task_logger

from ..choices import DesignRuleChoices
from .api_03 import run_api_03_test_rules
from .api_09 import run_api_09_test_rules
from .api_16 import run_api_16_test_rules
from .api_20 import run_api_20_test_rules
from .api_48 import run_api_48_test_rules
from .api_51 import run_api_51_test_rules

logger = get_task_logger(__name__)


def run_tests(session, api_endpoint):
    response = requests.get(api_endpoint)
    try:
        session.json_result = response.json()
    except JSONDecodeError:
        pass

    success_count = 0
    for test_option in session.test_version.test_rules.all():
        if test_option.rule_type == DesignRuleChoices.api_03:
            result = run_api_03_test_rules(session=session)
            if result.success:
                success_count += 1
        if test_option.rule_type == DesignRuleChoices.api_09:
            result = run_api_09_test_rules(session=session)
            if result.success:
                success_count += 1
        if test_option.rule_type == DesignRuleChoices.api_16:
            result = run_api_16_test_rules(session=session)
            if result.success:
                success_count += 1
        if test_option.rule_type == DesignRuleChoices.api_20:
            result = run_api_20_test_rules(session=session, api_endpoint=api_endpoint)
            if result.success:
                success_count += 1
        if test_option.rule_type == DesignRuleChoices.api_48:
            result = run_api_48_test_rules(session=session)
            if result.success:
                success_count += 1
        if test_option.rule_type == DesignRuleChoices.api_51:
            result = run_api_51_test_rules(session=session, api_endpoint=api_endpoint)
            if result.success:
                success_count += 1

    max_score = Decimal(session.test_version.test_rules.count())
    session.percentage_score = Decimal(100) / max_score * success_count
    session.save()
