from django.urls import path

from .views import DesignRulesDetailView, DesignRulesListView, DesignRulesCreateView, DesignRuleSessionDetailView, DesignRuleSessionCreateView
from . import apps

app_name = apps.AppConfig.__name__

urlpatterns = [
    path('', DesignRulesListView.as_view(), name='list'),
    path('create/', DesignRulesCreateView.as_view(), name='create'),
    path('<uuid:uuid>/', DesignRulesDetailView.as_view(), name='detail'),
    path('<uuid:uuid>/create/', DesignRuleSessionCreateView.as_view(), name='session_create'),
    path('<uuid:uuid_test_suite>/<uuid:uuid>/', DesignRuleSessionDetailView.as_view(), name='session_detail'),
]
