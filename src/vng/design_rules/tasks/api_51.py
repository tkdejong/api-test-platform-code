from urllib.parse import urlparse

from ..choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_api_51_test_rules(session, api_endpoint):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-51-publish-oas-at-the-base-uri-in-json-format

    3.15 API-51: Publish OAS at the base-URI in JSON-format

    Publish up-to-date documentation in the Open API Specification (OAS) at the publicly accessible root
    endpoint of the API in JSON format:

    https://service.omgevingswet.overheid.nl/publiek/catalogus/api/raadplegen/v1

    Makes the OAS relevant to v1 of the API available.

    Thus, the up-to-date documentation is linked to a unique location (that is always concurrent with
    the features available in the API).
    """
    from ..models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_51)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_51)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = "The API did not give a valid JSON output."
        result.save()
        return result

    has_match = False
    parsed_endpoint = urlparse(api_endpoint)
    paths = session.json_result.get("paths", {})
    for path, _methods in paths.items():
        if path == parsed_endpoint.path:
            has_match = True
            break

    servers = session.json_result.get("servers", [])
    for server in servers:
        if server.get("url", "") == api_endpoint:
            has_match = True

    if has_match:
        result.success = True
    else:
        result.success = False
        result.errors = "The endpoint does not seems to be the root endpoint"

    result.save()
    return result
