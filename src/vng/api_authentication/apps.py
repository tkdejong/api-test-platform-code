from django.apps import AppConfig


class ApiAuthenticationConfig(AppConfig):
    name = 'vng.api_authentication'

    def ready(self):
        from .authentication import CustomTokenAuthentication
        from .models import CustomToken
