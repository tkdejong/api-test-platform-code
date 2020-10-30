from rest_framework import routers
from django.urls import path, include

from vng.servervalidation import api_views, apps

app_name = apps.AppConfig.__name__


router = routers.DefaultRouter(trailing_slash=False)
router.register('provider-run', api_views.ServerRunViewSet, base_name='api_server-run')
router.register('postman-test', api_views.PostmanTestViewset, base_name='api_postman-test')


urlpatterns = router.urls + [
    path('provider-run-shield/<uuid:uuid>/', api_views.ResultServerViewShield.as_view(), name='api_server-run-shield'),
    path('provider-latest-badge/<uuid:uuid>/', api_views.ServerRunLatestResultView.as_view(), name='latest-badge'),
    path('provider-run/<uuid:uuid>/result', api_views.ResultServerView.as_view(), name='provider_result'),
]
