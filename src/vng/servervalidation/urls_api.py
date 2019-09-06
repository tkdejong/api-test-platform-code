
from rest_framework import routers, serializers, viewsets
from django.conf.urls import include
from django.urls import path, re_path

from . import api_views, apps
from ..utils.schema import schema_view

app_name = apps.AppConfig.__name__


router = routers.DefaultRouter()
router.register('provider-run', api_views.ServerRunViewSet, base_name='api_server-run')
router.register('postman-test', api_views.PostmanTestViewset, base_name='api_postman-test')


urlpatterns = [
    path('provider-run-shield/<uuid:uuid>/', api_views.ResultServerViewShield.as_view(), name='api_server-run-shield'),
    re_path(r'provider-latest-badge/(?P<name>[^/.]+)/(?P<user>[^/.]+)/', api_views.ServerRunLatestResultView.as_view(), name='latest-badge'),
    re_path(r'schema/openapi(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('schema', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('provider-run/<int:pk>/trigger/', api_views.TriggerServerRunView.as_view({'put': 'update'}), name='provider'),
    path('provider-run/<int:pk>/result/', api_views.ResultServerView.as_view(), name='provider_result'),
    path('', include((router.urls, 'server-api'), namespace='provider')),
]
