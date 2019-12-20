from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import views, apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    path('<int:api_id>/testscenarios/', views.TestScenarioList.as_view(), name='test-scenario_list'),
    path('<int:api_id>/testscenario/<int:pk>/', views.TestScenarioDetail.as_view(), name='testscenario-detail'),
    path('<int:api_id>/testscenario/<uuid:scenario_uuid>/update', views.TestScenarioUpdateView.as_view(), name='testscenario-update'),
    path('<int:api_id>/testscenario/<uuid:scenario_uuid>/delete', views.TestScenarioDeleteView.as_view(), name='testscenario-delete'),
    path('<int:api_id>/<int:test_id>/create/', views.SelectEnvironment.as_view(), name='server-run_select_environment'),
    path('<int:api_id>/<int:test_id>/<int:env_id>/create/endpoints', views.CreateEndpoint.as_view(), name='endpoints_create'),
    path('<int:api_id>/<int:test_id>/<int:env_id>/update/endpoints', views.UpdateEndpointView.as_view(), name='endpoints_update'),
    path('<int:api_id>/create/', views.ServerRunForm.as_view(), name='server-run_create_item'),
    path('<int:api_id>/postman/<int:pk>/', views.PostmanDownloadView.as_view(), name='postman_download'),
    path('<int:api_id>/<int:server_id>/stop/', views.StopServer.as_view(), name='server-run_stop'),
    path('<int:api_id>/<uuid:uuid>/trigger/', views.TriggerServerRun.as_view(), name='server-run_trigger'),
    path('<int:api_id>/<uuid:uuid>/schedule/', views.CreateSchedule.as_view(), name='server-run_create_schedule'),
    path('<int:api_id>/<uuid:uuid>/schedule/activate/', views.ScheduleActivate.as_view(), name='schedule_activate'),
    path('<int:api_id>/<uuid:uuid>/log_json/<int:test_result_pk>/', views.ServerRunLogJsonView.as_view(), name='server-run_detail_log_json'),
    path('<int:api_id>/<uuid:uuid>/log/<int:test_result_pk>/', views.ServerRunLogView.as_view(), name='server-run_detail_log'),
    path('<int:api_id>/<uuid:uuid>/pdf/<int:test_result_pk>', views.ServerRunPdfView.as_view(), name='server-run_detail_pdf'),
    path('<int:api_id>/<uuid:uuid>/update/', views.ServerRunOutputUpdate.as_view(), name='server-run_info-update'),
    path('<int:api_id>/<uuid:scenario_uuid>/<uuid:env_uuid>/update/', views.EnvironmentInfoUpdate.as_view(), name='environment_info-update'),
    path('<int:api_id>/<uuid:uuid>/', views.ServerRunOutputUuid.as_view(), name='server-run_detail'),
    path('<int:api_id>/', views.EnvironmentList.as_view(), name='environment_list'),
    path('<int:api_id>/<uuid:scenario_uuid>/<uuid:env_uuid>/', views.ServerRunList.as_view(), name='server-run_list'),
    path('<int:api_id>/<uuid:scenario_uuid>/<uuid:env_uuid>/latest/', views.LatestRunView.as_view(), name='server-run_latest'),
    path('<int:api_id>/scenario/create/', views.CreateTestScenarioView.as_view(), name='test-scenario_create_item'),
    path('generate/', views.CollectionFromOASView.as_view(), name='collection_generator'),
]
