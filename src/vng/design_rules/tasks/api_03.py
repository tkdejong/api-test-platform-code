from django.utils.translation import ugettext_lazy as _

from ..choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS", "SUMMARY", "DESCRIPTION", "$REF", "SERVERS"]


def run_api_03_test_rules(session):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-03-only-apply-default-http-operations
    3.3 API-03: Only apply default HTTP operations

    A RESTful API is an application programming interface that supports the default HTTP operations
    GET, PUT, POST, PATCH and DELETE.
    """
    from ..models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_03)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_03)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = _("The API did not give a valid JSON output.")
        result.save()
        return result

    paths = session.json_result.get("paths", {})
    methods_found = False
    errors = ""
    for path, methods in paths.items():
        for method, _options in methods.items():
            methods_found = True
            if method.upper() not in VALID_METHODS and method.upper() not in SKIPPED_METHODS:
                if errors:
                    errors += "\n"
                errors += _("not supported method, {}, found for path {}").format(method, path)

    if not methods_found:
        result.success = False
        result.errors = _("There are no methods found.")
    elif errors:
        result.success = False
        result.errors = errors
    else:
        result.success = True
    result.save()
    return result
