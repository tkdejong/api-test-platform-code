import rest_framework.authentication

from .models import CustomToken


class CustomTokenAuthentication(rest_framework.authentication.TokenAuthentication):
    model = CustomToken
