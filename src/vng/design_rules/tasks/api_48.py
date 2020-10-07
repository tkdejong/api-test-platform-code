from ..choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_api_48_test_rules(session):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-48-leave-off-trailing-slashes-from-api-endpoints
    3.14 API-48: Leave off trailing slashes from API endpoints

    URIs to retrieve collections of resources or individual resources don't include a trailing slash.
    A resource is only available at one endpoint/path. Resource paths end without a slash.
    """
    from ..models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_48)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_48)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = "The API did not give a valid JSON output."
        result.save()
        return result

    paths = session.json_result.get("paths", {})
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
