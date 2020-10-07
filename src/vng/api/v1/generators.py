from django.conf import settings
from drf_yasg.generators import OpenAPISchemaGenerator, EndpointEnumerator


class CustomEndpointEnumerator(EndpointEnumerator):
    """
    Add custom setting to exclude views
    """
    def should_include_endpoint(self, path, callback, app_name='', namespace='', url_name=None):
        print(path)
        for exclude_path in settings.DRF_YASG_EXCLUDE_PATHS:
            if path.startswith(exclude_path):
                print("return False")
                return False
        return super().should_include_endpoint(
            path, callback, app_name, namespace, url_name
        )


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """
    We want change default endpoint enumerator class
    """
    endpoint_enumerator_class = CustomEndpointEnumerator