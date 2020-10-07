from django.urls import include, path

from vng_api_common.schema import SchemaView


urlpatterns = [
    path('', SchemaView.without_ui(cache_timeout=0), name='api-root'),
    path('/schema', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('/auth/', include('vng.api.v1.api_authentication.urls', namespace='apiv1_auth')),
    path('/', include('vng.api.v1.testsession.urls', namespace='apiv1session')),
    path('/', include('vng.api.v1.servervalidation.urls', namespace='apiv1server')),
    path('/', include('vng.api.v1.open_api_inspector.urls', namespace='apiv1inspector')),
    path('/', include('vng.api.v1.design_rules.urls', namespace='api_v1_design_rules')),
]







