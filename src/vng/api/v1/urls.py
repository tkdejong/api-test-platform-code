from django.urls import include, path

from drf_spectacular.views import SpectacularJSONAPIView, SpectacularRedocView


urlpatterns = [
    path('/openapi.json', SpectacularJSONAPIView.as_view(), name='api-schema'),
    path('/schema', SpectacularRedocView.as_view(url_name="api-schema"), name='schema-redoc'),
    path('/auth/', include('vng.api.v1.api_authentication.urls', namespace='apiv1_auth')),
    path('/', include('vng.api.v1.testsession.urls', namespace='apiv1session')),
    path('/', include('vng.api.v1.servervalidation.urls', namespace='apiv1server')),
    path('/', include('vng.api.v1.open_api_inspector.urls', namespace='apiv1inspector')),
    path('/', include('vng.api.v1.design_rules.urls', namespace='api_v1_design_rules')),
]
