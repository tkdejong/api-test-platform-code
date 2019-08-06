from django.conf.urls import include, url
from django.urls import path

from . import apps, views

app_name = apps.AppConfig.__name__

urlpatterns = [
    url('', include('rest_auth.urls'), name='login-rest'),
    path('mytokens', views.TokenManager.as_view(), name='token-manager'),
]
