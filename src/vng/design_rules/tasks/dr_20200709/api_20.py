import re

from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices

REGEX_END_WITH_VERSION = r"\/v[\d]+$"
REGEX_OTHER = r"\/v[\d]+[\/]?[^\w.,]"
REGEX_MINOR_VERSION = r"(\/v[\d]+[.][\d+])"


def run_20200709_api_20(session, api_endpoint):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-20-include-the-major-version-number-only-in-ihe-uri
    3.13 API-20: Include the major version number only in ihe URI

    The URI of an API should include the major version number only. The minor and patch version numbers
    are in the response header of the message. Minor and patch versions have no impact on existing code,
    but major version do.
    """
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_20_20200709)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_20_20200709)

    searches = re.findall(REGEX_END_WITH_VERSION, api_endpoint, re.IGNORECASE)
    if searches:
        result.success = True
        result.save()
        return result

    searches = re.findall(REGEX_OTHER, api_endpoint, re.IGNORECASE)
    if searches:
        result.success = True
        result.save()
        return result

    searches = re.findall(REGEX_MINOR_VERSION, api_endpoint, re.IGNORECASE)
    if searches:
        result.success = False
        result.errors = [_("The api endpoint contains more than the major version number in the URI")]
    else:
        result.success = False
        result.errors = [_("The api endpoint does not contain a 'v*' in the url")]
    result.save()
    return result
