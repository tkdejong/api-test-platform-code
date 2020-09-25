import requests

from ..choices import DesignRuleChoices
from ..models import DesignRuleResult

PARAMETERS = ["PARAMETERS"]


def run_api_09_test_rules(session):
    """
    THis test is not working yet...
    Also I need to add the descroption and url of the rule.
    """

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_09)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_09)

    response = requests.get(session.api_endpoint)
    json_spec = response.json()
    paths = json_spec.get("paths")
    wrong_paths_with_method = ""
    for path, methods in paths.items():
        for method, options in methods.items():
            if method.upper() in PARAMETERS:
                print(options)
