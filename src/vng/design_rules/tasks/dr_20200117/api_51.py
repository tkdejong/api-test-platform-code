from urllib.parse import urlparse

from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_20200117_api_51(session, api_endpoint, is_json=False):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-51-publish-oas-at-the-base-uri-in-json-format
    """
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_51_20200117)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_51_20200117)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = [_("The API did not give a valid JSON output.")]
        result.save()
        return result

    if not is_json:
        result.success = False
        result.errors = [_("The API did not give a valid JSON output. It most likely was YAML")]
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
        result.errors = [_("The endpoint does not seems to be the root endpoint")]

    result.save()
    return result
