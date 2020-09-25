import requests

from ..choices import DesignRuleChoices
from ..models import DesignRuleResult

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_api_48_test_rules(session):
    """
    """

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_48)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_48)

    response = requests.get(session.api_endpoint)
    json_spec = response.json()
    paths = json_spec.get("paths")
    wrong_paths_with_method = ""
    for path, _methods in paths.items():
        if path.endswith('/'):
            if wrong_paths_with_method:
                wrong_paths_with_method += "\n"
            wrong_paths_with_method += "Path: {} ends with a slash".format(path)

    if wrong_paths_with_method:
        result.success = False
        result.errors = wrong_paths_with_method
    else:
        result.success = True
    result.save()
    return result
