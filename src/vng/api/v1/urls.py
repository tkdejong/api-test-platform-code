import os

from django.conf import settings
from django.urls import include, path

from vng_api_common.schema import OpenAPIV3RendererMixin, SchemaView as _SchemaView

from drf_yasg.renderers import SwaggerJSONRenderer
from .generators import CustomOpenAPISchemaGenerator


SPEC_RENDERERS = (
    type("SwaggerJSONRenderer", (OpenAPIV3RendererMixin, SwaggerJSONRenderer), {}),
)


class SchemaView(_SchemaView):
    generator_class = CustomOpenAPISchemaGenerator

    @property
    def _is_openapi_v2(self) -> bool:
        return False

    def get_renderers(self):
        if self._is_openapi_v2:
            return super().get_renderers()
        return [renderer() for renderer in SPEC_RENDERERS]

    def get_schema_path(self) -> str:
        return self.schema_path or os.path.join(
            settings.BASE_DIR, "src", "openapi.json"
        )


urlpatterns = [
    path('', SchemaView.without_ui(cache_timeout=0), name='api-root'),
    path('/schema', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('/auth/', include('vng.api.v1.api_authentication.urls', namespace='apiv1_auth')),
    path('/', include('vng.api.v1.testsession.urls', namespace='apiv1session')),
    path('/', include('vng.api.v1.servervalidation.urls', namespace='apiv1server')),
    path('/', include('vng.api.v1.open_api_inspector.urls', namespace='apiv1inspector')),
    path('/', include('vng.api.v1.design_rules.urls', namespace='api_v1_design_rules')),
]







