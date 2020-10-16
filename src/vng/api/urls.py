from django.conf.urls import include, url


urlpatterns = [
    url(r'^v1', include('vng.api.v1.urls')),
]
