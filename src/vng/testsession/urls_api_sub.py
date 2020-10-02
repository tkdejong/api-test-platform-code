from django.conf.urls import url

from vng.api.v1.testsession.views import RunTest
from . import apps
from ..base_url import base_urlpatterns
app_name = apps.AppConfig.__name__

urlpatterns = [
    url(r'^(?P<relative_url>[-\w|/|\.]*)$', RunTest.as_view(), name='run_test'),
] + base_urlpatterns
