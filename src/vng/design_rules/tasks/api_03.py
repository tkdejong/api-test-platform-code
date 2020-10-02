from ..choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


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
        result.errors = "The API did not give a valid JSON output."
        result.save()
        return result

    paths = session.json_result.get("paths", {})
    wrong_paths_with_method = {}
    for path, methods in paths.items():
        for method, _options in methods.items():
            if method.upper() not in VALID_METHODS and method.upper() not in SKIPPED_METHODS:
                if path in wrong_paths_with_method:
                    wrong_paths_with_method[path].append(method)
                else:
                    wrong_paths_with_method[path] = [method]

    print(wrong_paths_with_method)
    if wrong_paths_with_method:
        result.success = False
        result.errors = wrong_paths_with_method
    else:
        result.success = True
    result.save()
    return result
