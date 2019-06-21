from django.urls import include, path
from django.contrib.auth.decorators import login_required

from rest_framework import routers, serializers, viewsets

from . import views
from . import api_views, apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    path('', views.SessionListView.as_view(), name='sessions'),
    path('create', views.SessionFormView.as_view(), name='session_create'),
    path('postman/<int:pk>', views.PostmanDownloadView.as_view(), name='postman_download'),
    path('<int:session_id>/stop', views.StopSession.as_view(), name='stop_session'),
    path('<uuid:uuid>/report-pdf', views.SessionReportPdf.as_view(), name='session_report-pdf'),
    path('<uuid:uuid>/report', views.SessionReport.as_view(), name='session_report'),
    path('<uuid:uuid>/test-report-pdf/<int:pk>', views.SessionTestReportPDF.as_view(), name='session-test_report-pdf'),
    path('<uuid:uuid>/test-report/<int:pk>', views.SessionTestReport.as_view(), name='session-test_report'),
    path('<uuid:uuid>/log/<uuid:log_uuid>', views.SessionLogDetailView.as_view(), name='session_log-detail'),
    path('<uuid:uuid>/', views.SessionLogView.as_view(), name='session_log'),
    path('<int:session_id>/update', views.SessionLogUpdateView.as_view(), name='session_update'),
    path('sessiontype/<int:pk>', views.SessionTypeDetail.as_view(), name='session_type-detail'),
]
