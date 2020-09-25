import requests

from ..choices import DesignRuleChoices
from ..models import DesignRuleResult


def run_api_16_test_rules(session):
    """
    """

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_16)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_16)

    response = requests.get(session.api_endpoint)
    json_spec = response.json()
    version = json_spec.get("openapi")
    try:
        split_version = version.split('.')
        major_int = int(split_version[0])
        _minor_int = int(split_version[1])
        _bug_int = int(split_version[2])

        if major_int >= 3:
            result.success = True
        else:
            result.success = False
            result.errors = "The version ({}) is not higher than or equal to OAS 3.0"
    except Exception as e:
        result.success = False
        result.errors = "This is not a valid OAS api version or OAS api version is not found"
    finally:
        result.save()
        return result
