import re
import requests

from ..choices import DesignRuleChoices
from ..models import DesignRuleResult

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_api_20_test_rules(session):
    """
    """

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_20)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_20)

    searches = re.search("(\/v[\d]+[\/]?[^\w.,])", session.api_endpoint)
    if searches:
        result.success = True
        result.save()
        return result

    searches = re.search("(\/v[\d]+[.][\d+])", session.api_endpoint)
    if searches:
        result.success = False
        result.errors = "The api endpoint contains more than the major version number in the URI"
    else:
        result.success = False
        result.errors = "The api endpoint does not contain a 'v*' in the url"
    result.save()
    return result
