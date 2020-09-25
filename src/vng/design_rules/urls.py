from django.urls import path

from .views import DesignRulesDetailView, DesignRulesListView, DesignRulesCreateView
from . import apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    path('<int:api_id>/', DesignRulesListView.as_view(), name='list'),
    path('<int:api_id>/create/', DesignRulesCreateView.as_view(), name='create'),
    path('<int:api_id>/<uuid:uuid>/', DesignRulesDetailView.as_view(), name='detail'),
    # path('<int:api_id>/postman/<int:pk>/', views.PostmanDownloadView.as_view(), name='postman_download'),
    # path('<int:api_id>/<uuid:uuid>/stop/', views.StopSession.as_view(), name='stop_session'),
    # path('<int:api_id>/<uuid:uuid>/report-pdf/', views.SessionReportPdf.as_view(), name='session_report-pdf'),
    # path('<int:api_id>/<uuid:uuid>/report/', views.SessionReport.as_view(), name='session_report'),
    # path('<int:api_id>/<uuid:uuid>/test-report-pdf/<int:pk>/', views.SessionTestReportPDF.as_view(), name='session-test_report-pdf'),
    # path('<int:api_id>/<uuid:uuid>/test-report/<int:pk>/', views.SessionTestReport.as_view(), name='session-test_report'),
    # path('<int:api_id>/<uuid:uuid>/log/<uuid:log_uuid>/', views.SessionLogDetailView.as_view(), name='session_log-detail'),
    # path('<int:api_id>/<uuid:uuid>/', views.SessionLogView.as_view(), name='session_log'),
    # path('<int:api_id>/<uuid:uuid>/update/', views.SessionLogUpdateView.as_view(), name='session_update'),
    # path('<int:api_id>/sessiontype/<int:pk>/', views.SessionTypeDetail.as_view(), name='session_type-detail'),
]
