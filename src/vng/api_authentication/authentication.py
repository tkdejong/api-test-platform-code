from rest_framework.authentication import TokenAuthentication


class CustomTokenAuthentication(TokenAuthentication):
    def get_model(self):
        from .models import CustomToken
        return CustomToken
