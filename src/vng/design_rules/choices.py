from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class DesignRuleChoices(DjangoChoices):
    # api_01 = ChoiceItem("api_01", _("API-01: Operations are Safe and/or Idempotent"))
    # api_02 = ChoiceItem("api_02", _("API-02: Do not maintain state information at the server"))
    api_03 = ChoiceItem("api_03", _("API-03: Only apply default HTTP operations"))
    # api_04 = ChoiceItem("api_04", _("API-04: Define interfaces in Dutch unless there is an official English glossary"))
    # api_05 = ChoiceItem("api_05", _("API-05: Use plural nouns to indicate resources"))
    # api_06 = ChoiceItem("api_06", _("API-06: Create relations of nested resources within the endpoint"))
    api_09 = ChoiceItem("api_09", _("API-09: Implement custom representation if supported"))
    # api_10 = ChoiceItem("api_10", _("API-10: Implement operations that do not fit the CRUD model as sub-resources"))
    api_16 = ChoiceItem("api_16", _("API-16: Use OAS 3.0 for documentation"))
    # api_17 = ChoiceItem("api_17", _("API-17: Publish documentation in Dutch unless there is existing documentation in English or there is an official English glossary available"))
    # api_18 = ChoiceItem("api_18", _("API-18: Include a deprecation schedule when publishing API changes"))
    # api_19 = ChoiceItem("api_19", _("API-19: Allow for a maximum 1 year transition period to a new API version"))
    api_20 = ChoiceItem("api_20", _("API-20: Include the major version number only in ihe URI"))
    api_48 = ChoiceItem("api_48", _("API-48: Leave off trailing slashes from API endpoints"))
    api_51 = ChoiceItem("api_51", _("API-51: Publish OAS at the base-URI in JSON-format"))
