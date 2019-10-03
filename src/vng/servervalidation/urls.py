from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import views, apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    path('testscenario/<int:pk>/', views.TestScenarioDetail.as_view(), name='testscenario-detail'),
    path('<int:test_id>/create/', views.SelectEnvironment.as_view(), name='server-run_select_environment'),
    path('<int:test_id>/<int:env_id>/create/endpoints', views.CreateEndpoint.as_view(), name='endpoints_create'),
    path('create/', views.ServerRunForm.as_view(), name='server-run_create_item'),
    path('postman/<int:pk>/', views.PostmanDownloadView.as_view(), name='postman_download'),
    path('scheduled/<uuid:uuid>/', views.ServerRunListScheduled.as_view(), name='server-run_list_scheduled'),
    path('scheduled/', views.ScheduledTestScenarioList.as_view(), name='scheduled-test-scenario_list'),
    path('<int:server_id>/stop/', views.StopServer.as_view(), name='server-run_stop'),
    path('scheduled/<uuid:uuid>/trigger/', views.TriggerServerRunScheduled.as_view(), name='scheduled-server-run_trigger'),
    path('<uuid:uuid>/trigger/', views.TriggerServerRun.as_view(), name='server-run_trigger'),
    path('scheduled/<uuid:uuid>/stop/', views.ScheduleActivate.as_view(), name='schedule_activate'),
    path('<uuid:uuid>/log_json/<int:test_result_pk>/', views.ServerRunLogJsonView.as_view(), name='server-run_detail_log_json'),
    path('<uuid:uuid>/log/<int:test_result_pk>/', views.ServerRunLogView.as_view(), name='server-run_detail_log'),
    path('<uuid:uuid>/pdf/<int:test_result_pk>', views.ServerRunPdfView.as_view(), name='server-run_detail_pdf'),
    path('<uuid:uuid>/update/', views.ServerRunOutputUpdate.as_view(), name='server-run_info-update'),
    path('<uuid:uuid>/', views.ServerRunOutputUuid.as_view(), name='server-run_detail'),
    path('', views.TestScenarioList.as_view(), name='test-scenario_list'),
    path('<uuid:scenario_uuid>/<uuid:env_uuid>/', views.ServerRunList.as_view(), name='server-run_list'),
    # path('', views.ServerRunList.as_view(), name='server-run_list'),
]
