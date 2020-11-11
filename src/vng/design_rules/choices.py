from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices

api_03_description = """A RESTful API is an application programming interface that supports the default HTTP operations GET, PUT, POST, PATCH and DELETE."""
api_09_description = """Provide a comma-separated list of field names using the query parameter fields te retrieve a custom representation. In case non-existent field names are passed, a 400 Bad Request error message is returned."""
api_16_description = """Publish specifications (documentation) as Open API Specification (OAS) 3.0 or higher."""
api_20_description = """The URI of an API should include the major version number only. The minor and patch version numbers are in the response header of the message. Minor and patch versions have no impact on existing code, but major version do."""
api_48_description = """URIs to retrieve collections of resources or individual resources don't include a trailing slash. A resource is only available at one endpoint/path. Resource paths end without a slash."""
api_51_description = """Publish up-to-date documentation in the Open API Specification (OAS) at the publicly accessible root endpoint of the API in JSON format:
https://service.omgevingswet.overheid.nl/publiek/catalogus/api/raadplegen/v1
Makes the OAS relevant to v1 of the API available. Thus, the up-to-date documentation is linked to a unique location (that is always concurrent with the features available in the API)."""


class DesignRuleChoices(DjangoChoices):
    # api_01 = ChoiceItem("api_01", _("API-01: Operations are Safe and/or Idempotent"))
    # api_02 = ChoiceItem("api_02", _("API-02: Do not maintain state information at the server"))
    api_03 = ChoiceItem(
        "api_03",
        _("API-03: Only apply default HTTP operations"),
        url="https://docs.geostandaarden.nl/api/API-Designrules/#api-03-only-apply-default-http-operations",
        description=api_03_description,
    )
    # api_04 = ChoiceItem("api_04", _("API-04: Define interfaces in Dutch unless there is an official English glossary"))
    # api_05 = ChoiceItem("api_05", _("API-05: Use plural nouns to indicate resources"))
    # api_06 = ChoiceItem("api_06", _("API-06: Create relations of nested resources within the endpoint"))
    api_09 = ChoiceItem(
        "api_09",
        _("API-09: Implement custom representation if supported"),
        url="https://docs.geostandaarden.nl/api/API-Designrules/#api-09-implement-custom-representation-if-supported",
        description=api_09_description,
    )
    # api_10 = ChoiceItem("api_10", _("API-10: Implement operations that do not fit the CRUD model as sub-resources"))
    api_16 = ChoiceItem(
        "api_16",
        _("API-16: Use OAS 3.0 for documentation"),
        url="https://docs.geostandaarden.nl/api/API-Designrules/#api-16-use-oas-3-0-for-documentation",
        description=api_16_description,
    )
    # api_17 = ChoiceItem("api_17", _("API-17: Publish documentation in Dutch unless there is existing documentation in English or there is an official English glossary available"))
    # api_18 = ChoiceItem("api_18", _("API-18: Include a deprecation schedule when publishing API changes"))
    # api_19 = ChoiceItem("api_19", _("API-19: Allow for a maximum 1 year transition period to a new API version"))
    api_20 = ChoiceItem(
        "api_20",
        _("API-20: Include the major version number only in ihe URI"),
        url="https://docs.geostandaarden.nl/api/API-Designrules/#api-20-include-the-major-version-number-only-in-ihe-uri",
        description=api_20_description,
    )
    api_48 = ChoiceItem(
        "api_48",
        _("API-48: Leave off trailing slashes from API endpoints"),
        url="https://docs.geostandaarden.nl/api/API-Designrules/#api-48-leave-off-trailing-slashes-from-api-endpoints",
        description=api_48_description,
    )
    api_51 = ChoiceItem(
        "api_51",
        _("API-51: Publish OAS at the base-URI in JSON-format"),
        url="https://docs.geostandaarden.nl/api/API-Designrules/#api-51-publish-oas-at-the-base-uri-in-json-format",
        description=api_51_description,
    )
