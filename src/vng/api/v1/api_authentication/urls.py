from django.conf.urls import url
from django.urls import path
from rest_auth.views import (
    UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)

from vng.apiAuthentication import apps, views

app_name = apps.AppConfig.__name__

urlpatterns = [
    url(r'^password/reset$', PasswordResetView.as_view(), name='rest_password_reset'),
    url(r'^password/reset/confirm$', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),

    # URLs that require a user to be logged in with a valid session / token.
    url(r'^user$', UserDetailsView.as_view(), name='rest_user_details'),
    url(r'^password/change$', PasswordChangeView.as_view(), name='rest_password_change'),
    url(r'^login$', views.CustomLoginView.as_view(), name='rest_login'),
    url(r'^logout$', views.CustomLogoutView.as_view(), name='rest_logout'),
    path('mytokens', views.TokenManager.as_view(), name='token-manager'),
]
