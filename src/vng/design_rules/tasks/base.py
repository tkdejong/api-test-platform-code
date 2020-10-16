from json import JSONDecodeError
from decimal import Decimal

import requests
from celery.utils.log import get_task_logger

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

    # Can be tested without a json endpoint
    result_20 = run_api_20_test_rules(session=session, api_endpoint=api_endpoint)
    result_51 = run_api_51_test_rules(session=session, api_endpoint=api_endpoint)
    result_16 = run_api_16_test_rules(session=session)
    result_03 = run_api_03_test_rules(session=session)
    result_48 = run_api_48_test_rules(session=session)
    result_09 = run_api_09_test_rules(session=session)

    count_score = 0
    max_score = Decimal(6)
    for success in [result_20.success, result_51.success, result_16.success, result_03.success, result_48.success, result_09.success]:
        if success:
            count_score += 1

    session.percentage_score = Decimal(100) / max_score * count_score
    session.save()
