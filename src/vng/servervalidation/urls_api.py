
from django.urls import path, include
from rest_framework import routers, serializers, viewsets

from . import api_views, apps
from ..utils.schema import schema_view

app_name = apps.AppConfig.__name__


router = routers.DefaultRouter()
router.register('provider-run', api_views.ServerRunViewSet, base_name='api_server-run')


urlpatterns = [
    path('provider-run-shield/<uuid:uuid>', api_views.ResultServerViewShield.as_view(), name='api_server-run-shield'),
    path('schema', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('provider-run/<int:pk>/trigger', api_views.TriggerServerRunView.as_view({'put': 'update'}), name='provider'),
    path('provider-run/<int:pk>/result', api_views.ResultServerView.as_view(), name='provider_result'),
    path('', include((router.urls, 'server-api'), namespace='provider')),
]
