from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from rest_framework import routers, serializers, viewsets

from . import views
from . import api_views, apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    url('^$', views.SessionListView.as_view(), name='sessions'),
    url('^create', views.SessionFormView.as_view(), name='session_create'),
    url(r'^postman/(?P<pk>[0-9]+)', views.PostmanDownloadView.as_view(), name='postman_download'),
    url(r'^(?P<uuid>[0-9a-f-]+)/stop', views.StopSession.as_view(), name='stop_session'),
    url(r'^(?P<uuid>[0-9a-f-]+)/report-pdf', views.SessionReportPdf.as_view(), name='session_report-pdf'),
    url(r'^(?P<uuid>[0-9a-f-]+)/report', views.SessionReport.as_view(), name='session_report'),
    url(r'^(?P<uuid>[0-9a-f-]+)/test-report-pdf/(?P<pk>[0-9]+)$', views.SessionTestReportPDF.as_view(), name='session-test_report-pdf'),
    url(r'^(?P<uuid>[0-9a-f-]+)/test-report/(?P<pk>[0-9]+)', views.SessionTestReport.as_view(), name='session-test_report'),
    url(r'^(?P<uuid>[0-9a-f-]+)/log/(?P<log_uuid>[0-9a-f-]+)', views.SessionLogDetailView.as_view(), name='session_log-detail'),
    url(r'^(?P<uuid>[0-9a-f-]+)/', views.SessionLogView.as_view(), name='session_log'),
    url(r'^sessiontype/(?P<pk>[0-9]+)/', views.SessionTypeDetail.as_view(), name='session_type-detail'),
]
