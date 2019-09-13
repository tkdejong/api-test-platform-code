from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import views, apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    path('testscenario/<int:pk>/', views.TestScenarioDetail.as_view(), name='testscenario-detail'),
    path('<int:test_id>/create/', views.CreateEndpoint.as_view(), name='server-run_create'),
    path('create/', views.ServerRunForm.as_view(), name='server-run_create_item'),
    path('postman/<int:pk>/', views.PostmanDownloadView.as_view(), name='postman_download'),
    path('scheduled/', views.ServerRunListScheduled.as_view(), name='server-run_list_scheduled'),
    path('<int:server_id>/stop/', views.StopServer.as_view(), name='server-run_stop'),
    path('<int:server_id>/trigger/', views.TriggerServerRun.as_view(), name='server-run_trigger'),
    path('<uuid:uuid>/log_json/<int:test_result_pk>/', views.ServerRunLogJsonView.as_view(), name='server-run_detail_log_json'),
    path('<uuid:uuid>/log/<int:test_result_pk>/', views.ServerRunLogView.as_view(), name='server-run_detail_log'),
    path('<uuid:uuid>/pdf/<int:test_result_pk>', views.ServerRunPdfView.as_view(), name='server-run_detail_pdf'),
    path('<uuid:uuid>/update/', views.ServerRunOutputUpdate.as_view(), name='server-run_info-update'),
    path('<uuid:uuid>/', views.ServerRunOutputUuid.as_view(), name='server-run_detail'),
    path('', views.ServerRunList.as_view(), name='server-run_list'),
]
