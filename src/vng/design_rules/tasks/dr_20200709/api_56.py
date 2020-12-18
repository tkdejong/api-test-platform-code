from urllib.parse import urlparse

import semver

from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_20200709_api_56(session):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-51-publish-oas-at-the-base-uri-in-json-format
    """
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_56_20200709)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_56_20200709)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = [_("The API did not give a valid JSON output.")]
        result.save()
        return result

    version = session.json_result.get("openapi", session.json_result.get("swagger"))
    if not version:
        result.success = False
        result.errors = [_("There is no openapi version found.")]
        result.save()
        return result

    try:
        semver.VersionInfo.parse(version)
        result.success = True
    except ValueError:
        result.success = False
        result.errors = [_("The given version does not resamble a SemVer version.")]

    result.save()
    return result
