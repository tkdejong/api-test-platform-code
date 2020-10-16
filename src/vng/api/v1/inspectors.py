from collections import OrderedDict

from drf_yasg import openapi
from vng_api_common.inspectors.view import AutoSchema as _AutoSchema, response_header


class AutoSchema(_AutoSchema):
    @property
    def model(self):
        try:
            if hasattr(self.view, "get_queryset"):
                qs = self.view.get_queryset()
                return qs.model
        finally:
            return None

    def get_response_schemas(self, response_serializers):
        responses = super().get_response_schemas(response_serializers)
        if not hasattr(self.view, "deprecation_message"):
            return responses

        return responses

    def is_deprecated(self):
        deprecation_message = getattr(self.view, "deprecation_message", None)
        return bool(deprecation_message) or super().is_deprecated()
