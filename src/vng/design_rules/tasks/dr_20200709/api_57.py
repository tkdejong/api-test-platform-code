from urllib.parse import urlparse

import semver

from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices

VALID_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
SKIPPED_METHODS = ["PARAMETERS"]


def run_20200709_api_57(session, response):
    """
    https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-57
    """
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_51_20200709)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_51_20200709)

    if "API-Version" not in response.headers:
        result.success = False
        result.errors = [_("The headers is missing. Make sure that the 'API-Version' is given.")]
    else:
        result.success = True
    result.save()
    return result
