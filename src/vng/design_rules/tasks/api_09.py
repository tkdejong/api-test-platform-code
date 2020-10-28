from django.utils.translation import ugettext_lazy as _

import requests

from ..choices import DesignRuleChoices

PARAMETERS = "PARAMETERS"


def run_api_09_test_rules(session, api_endpoint, token="efa36f1f00c7081ae8eb0f1aafd01985b1f6fa76"):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-09-implement-custom-representation-if-supported
    3.7 API-09: Implement custom representation if supported

    Provide a comma-separated list of field names using the query parameter fields te retrieve a custom
    representation. In case non-existent field names are passed, a 400 Bad Request error message is returned.
    """
    from ..models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_09)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_09)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = _("The API did not give a valid JSON output.")
        result.save()
        return result

    paths = session.json_result.get("paths", {})
    errors = ""
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
                                if errors:
                                    errors += "\n"
                                errors += "there is no schema for the field parameter found for path: {}, method: {}".format(path, method)
                                continue
                            enum = schema.get('enum')
                            if not enum:
                                if errors:
                                    errors += "\n"
                                errors += "there are no field options found for path: {}, method: {}".format(path, method)
                                continue

                            # Make api request test
                            if method.upper() == "GET":
                                url = "{}{}?fields=this_field_should_not_exist".format(api_endpoint, path)
                                headers = {'Authorization': 'Token 1519eba39c5828ff9a3f28a552f57740bb69df69'}
                                response = requests.get(url=url, headers=headers)
                                print("===========================================================")
                                print(response.status_code)
                                print(dir(response))
                                print(response.text)
                                if response.status_code != 400:
                                    errors += "Failed with status: {}. The status should be 400".format(response.status_code)

    if not found_fields:
        result.success = True
    elif errors:
        result.success = False
        result.errors = errors
    else:
        result.success = True

    result.save()
    return result
