from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem


API_09_DESCRIPTION = """Provide a comma-separated list of field names using the query parameter fields te retrieve a custom representation. In case non-existent field names are passed, a 400 Bad Request error message is returned."""
API_51_DESCRIPTION = """Publish up-to-date documentation in the Open API Specification (OAS) at the publicly accessible root endpoint of the API in JSON format:
https://service.omgevingswet.overheid.nl/publiek/catalogus/api/raadplegen/v1
Makes the OAS relevant to v1 of the API available.
Thus, the up-to-date documentation is linked to a unique location (that is always concurrent with the features available in the API)."""

api_09_20200117 = ChoiceItem(
    "api_09", _("API-09 V-17-01-2020: Implement custom representation if supported"),
    description=API_09_DESCRIPTION, url="https://docs.geostandaarden.nl/api/API-Designrules/#api-09-implement-custom-representation-if-supported",
)
api_51_20200117 = ChoiceItem(
    "api_51", _("API-51 V-17-01-2020: Publish OAS at the base-URI in JSON-format"),
    description=API_51_DESCRIPTION, url="https://docs.geostandaarden.nl/api/API-Designrules/#api-51-publish-oas-at-the-base-uri-in-json-format",
)
