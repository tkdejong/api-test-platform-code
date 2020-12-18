from urllib.parse import urlparse

from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_20200709_api_51(session, response, correct_location=False, is_json=False):
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
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_51_20200709)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_51_20200709)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = [_("The API did not give a valid JSON output.")]
        result.save()
        return result

    warnings = []
    errors = []
    if not correct_location:
        warnings.append(_("The api endpoint is only working on the root endpoint. whilst it should be on openapi.json"))

    if not is_json:
        warnings.append(_("The API did not give a valid JSON output. It most likely was YAML"))

    cors_headers = response.headers.get("Access-Control-Allow-Origin")
    parsed_url = urlparse(response.url)
    host = "{}://{}".format(parsed_url.scheme, parsed_url.netloc)
    if not cors_headers:
        errors.append(_("There are no CORS headers set. Please make sure that CORS headers are set."))
    elif cors_headers in [host, "{}/".format(host)]:
        errors.append(_("The CORS headers only allow the requested domain. Please make sure that it can be loaded from outside the domain"))

    if warnings:
        result.warnings = warnings

    if errors:
        result.success = False
        result.errors = errors
    else:
        result.success = True

    result.save()
    return result
