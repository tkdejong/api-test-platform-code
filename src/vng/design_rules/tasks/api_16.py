from ..choices import DesignRuleChoices


def run_api_16_test_rules(session):
    """
    https://docs.geostandaarden.nl/api/API-Designrules/#api-16-use-oas-3-0-for-documentation
    3.9 API-16: Use OAS 3.0 for documentation

    Publish specifications (documentation) as Open API Specification (OAS) 3.0 or higher.
    """
    from ..models import DesignRuleResult

    # We do not want double results for the same design rule
    base_qs = session.results.filter(rule_type=DesignRuleChoices.api_16)
    if base_qs.exists():
        return base_qs.first()

    result = DesignRuleResult(design_rule=session, rule_type=DesignRuleChoices.api_16)

    # Only execute when there is a JSON response
    if not session.json_result:
        result.success = False
        result.errors = "The API did not give a valid JSON output."
        result.save()
        return result

    version = session.json_result.get("openapi")
    if not version:
        result.success = False
        result.errors = "There is no openapi version found."
        result.save()
        return result

    try:
        split_version = version.split('.')
        major_int = int(split_version[0])
        _minor_int = int(split_version[1])
        _bug_int = int(split_version[2])

        if major_int >= 3:
            result.success = True
        else:
            result.success = False
            result.errors = "The version ({}) is not higher than or equal to OAS 3.0"
    except Exception as e:
        result.success = False
        result.errors = "This is not a valid OAS api version."
    finally:
        result.save()
        return result
