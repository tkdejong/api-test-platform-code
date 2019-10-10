from django.urls import path

from . import views
from . import apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    path('<int:api_id>/', views.SessionListView.as_view(), name='sessions'),
    path('<int:api_id>/create/', views.SessionFormView.as_view(), name='session_create'),
    path('postman/<int:pk>/', views.PostmanDownloadView.as_view(), name='postman_download'),
    path('<uuid:uuid>/stop/', views.StopSession.as_view(), name='stop_session'),
    path('<uuid:uuid>/report-pdf/', views.SessionReportPdf.as_view(), name='session_report-pdf'),
    path('<uuid:uuid>/report/', views.SessionReport.as_view(), name='session_report'),
    path('<uuid:uuid>/test-report-pdf/<int:pk>/', views.SessionTestReportPDF.as_view(), name='session-test_report-pdf'),
    path('<uuid:uuid>/test-report/<int:pk>/', views.SessionTestReport.as_view(), name='session-test_report'),
    path('<uuid:uuid>/log/<uuid:log_uuid>/', views.SessionLogDetailView.as_view(), name='session_log-detail'),
    path('<uuid:uuid>/', views.SessionLogView.as_view(), name='session_log'),
    path('<uuid:uuid>/update/', views.SessionLogUpdateView.as_view(), name='session_update'),
    path('sessiontype/<int:pk>/', views.SessionTypeDetail.as_view(), name='session_type-detail'),
]
