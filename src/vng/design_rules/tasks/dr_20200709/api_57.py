from urllib.parse import urlparse

import semver

from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices


def run_20200709_api_57(session, response):
    """
    https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-57
    """
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_57_20200709)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_57_20200709)

    if not response:
        result.success = False
        result.error = [_("Unable to obtain valid response from API.")]
    elif "API-Version" not in response.headers:
        result.success = False
        result.errors = [_("The headers is missing. Make sure that the 'API-Version' is given.")]
    else:
        result.success = True
    result.save()
    return result
