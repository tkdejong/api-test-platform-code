from django.utils.translation import ugettext_lazy as _

from ...choices import DesignRuleChoices

PARAMETERS = "PARAMETERS"


def run_20200117_api_09(session):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-09-implement-custom-representation-if-supported
    """
    from ...models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_09_20200117)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_09_20200117)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = [_("The API did not give a valid JSON output.")]
        result.save()
        return result

    paths = session.json_result.get("paths", {})
    errors = []
    found_fields = False
    for path, methods in paths.items():
        for method, options in methods.items():
            if isinstance(options, list):
                continue

            for option, parameters in options.items():
                if option.upper() == PARAMETERS:
                    for parameter in parameters:
                        if parameter.get('name') == "fields":
                            found_fields = True
                            schema = parameter.get('schema')
                            if not schema:
                                errors.append(_("there is no schema for the field parameter found for path: {}, method: {}").format(path, method))
                                continue
                            items = schema.get('items')
                            if not items:
                                errors.append(_("there are no field options found for path: {}, method: {}").format(path, method))
                                continue

                            any_of = items.get('anyOf')
                            if not any_of:
                                errors.append(_("there are no field options found for path: {}, method: {}").format(path, method))
                                continue

    if not found_fields:
        result.success = True
    elif errors:
        result.success = False
        result.errors = errors
    else:
        result.success = True

    result.save()
    return result
