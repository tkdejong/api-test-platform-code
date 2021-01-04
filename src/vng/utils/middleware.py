from django.conf import settings


class APIVersionHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['API-Version'] = settings.SPECTACULAR_SETTINGS.get("VERSION")
        return response
