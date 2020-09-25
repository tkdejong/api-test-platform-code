import requests

from ..choices import DesignRuleChoices
from ..models import DesignRuleResult

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_api_51_test_rules(session):
    """
    """

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_51)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_51)
    if not session.api_endpoint.endswith("v1"):
        result.success = False
        result.errors = "The api endpoint is not a base endpoint. It should end in a version."
        result.save()
        return result

    response = requests.get(session.api_endpoint)
    try:
        _json_spec = response.json()
        result.success = True
        result.save()
        return result
    except Exception as e:
        print(e)
        result.success = False
        result.errors = "This endpoint is not JSON"
        return result
