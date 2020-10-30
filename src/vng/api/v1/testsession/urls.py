from django.urls.base import reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework import routers

from django.urls import path

from vng.testsession import apps
from .views import SessionViewSet, SessionTypesViewSet, ExposedUrlView, SessionViewStatusSet, ResultSessionView, ResultTestsessionViewShield, StopSessionView


app_name = apps.AppConfig.__name__


router = routers.SimpleRouter(trailing_slash=False)
router.register('testsessions', SessionViewSet, 'test_session')
router.register('sessiontypes', SessionTypesViewSet, 'session_types')
router.register('exposed_url', ExposedUrlView, 'exposed_url')
router.register('status', SessionViewStatusSet, 'test_session-status')


urlpatterns = router.urls + [
    path('testsession-run-shield/<uuid:uuid>', ResultTestsessionViewShield.as_view(), name='testsession-shield'),
    path('testsession-run-shield/<uuid:uuid>/', RedirectView.as_view(url=reverse_lazy("apiv1session:testsession-shield")), name='testsession-shield-with-slash'),
    path('testsessions/<uuid:uuid>/stop', StopSessionView.as_view(), name='stop_session'),
    path('testsessions/<uuid:uuid>/result', ResultSessionView.as_view(), name='result_session'),
]
