from django.conf.urls import url

from vng.openApiInspector import api_views, apps

app_name = apps.AppConfig.__name__


urlpatterns = [
    url('openAPIinspector', api_views.OpenApiInspectionAPIView.as_view(), name='openAPIinspection'),
]
