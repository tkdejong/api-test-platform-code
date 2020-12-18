from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem


API_03_DESCRIPTION = """The HTTP specification [rfc7231] and the later introduced PATCH method specification [rfc5789] offer a set of standard methods, where every method is designed with explicit semantics. Adhering to the HTTP specification is crucial, since HTTP clients and middleware applications rely on standardized characteristics. Therefore, resources must be retrieved or manipulated using standard HTTP methods."""
API_09_DESCRIPTION = """Provide a comma-separated list of field names using the query parameter fields te retrieve a custom representation. In case non-existent field names are passed, a 400 Bad Request error message is returned."""
API_16_DESCRIPTION = """The OpenAPI Specification (OAS) [OPENAPIS] defines a standard, language-agnostic interface to RESTful APIs which allows both humans and computers to discover and understand the capabilities of the service without access to source code, documentation, or through network traffic inspection. When properly defined, a consumer can understand and interact with the remote service with a minimal amount of implementation logic.
API documentation must be provided in the form of an OpenAPI definition document which conforms to the OpenAPI Specification (from v3 onwards). As a result, a variety of tools can be used to render the documentation (e.g. Swagger UI or ReDoc) or automate tasks such as testing or code generation. The OAS document should provide clear descriptions and examples."""
API_20_DESCRIPTION = """The URI of an API (base path) must include the major version number, prefixed by the letter v. This allows the exploration of multiple versions of an API in the browser. The minor and patch version numbers are not part of the URI and may not have any impact on existing client implementations."""
API_48_DESCRIPTION = """According to the URI specification [rfc3986], URIs may contain a trailing slash. However, for REST APIs this is considered as a bad practice since a URI including or excluding a trailing slash might be interpreted as different resources (which is strictly speaking the correct interpretation).
To avoid confusion and ambiguity, a URI must never contain a trailing slash. When requesting a resource including a trailing slash, this must result in a 404 (not found) error response and not a redirect. This enforces API consumers to use the correct URI."""
API_51_DESCRIPTION = """To make the OAS document easy to find and to facilitate self-discovering clients, there should be one standard location where the OAS document is available for download. Clients (such as Swagger UI or ReDoc) must be able to retrieve the document without having to authenticate. Furthermore, the CORS policy for this URI must allow external domains to read the documentation from a browser environment.
The standard location for the OAS document is a URI called openapi.json or openapi.yaml within the base path of the API. This can be convenient, because OAS document updates can easily become part of the CI/CD process.
At least the JSON format must be supported. When having multiple (major) versions of an API, every API should provide its own OAS document(s)."""
API_53_DESCRIPTION = """An API should not expose implementation details of the underlying application. The primary motivation behind this design rule is that an API design must focus on usability for the client, regardless of the implementation details under the hood. The API, application and infrastructure need to be able to evolve independently to ease the task of maintaining backwards compatibility for APIs during an agile development process.
A few examples of implementation details:
    The API design should not necessarily be a 1-on-1 mapping of the underlying domain- or persistence model
    The API should not expose information about the technical components being used, such as development platforms/frameworks or database systems
    The API should offer client-friendly attribute names and values, while persisted data may contain abbreviated terms or serializations which might be cumbersome for consumption
"""
API_54_DESCRIPTION = """Because a collection resource represents multiple things, the path segment describing the name of the collection resource must be written in the plural form.
Example collection resources, describing a list of things:
https://api.example.org/v1/gebouwen
https://api.example.org/v1/vergunningen

Singular resources contained within a collection resource are generally named by appending a path segment for the identification of each individual resource.
Example singular resource, contained within a collection resource:
https://api.example.org/v1/gebouwen/3b9710c4-6614-467a-ab82-36822cf48db1
https://api.example.org/v1/vergunningen/d285e05c-6b01-45c3-92d8-5e19a946b66f

Singular resources that stand on their own, i.e. which are not contained within a collection resource, must be named with a path segment that is written in the singular form.
Example singular resource describing the profile of the currently authenticated user:
https://api.example.org/v1/gebruikersprofiel
"""
API_55_DESCRIPTION = """When releasing new (major, minor or patch) versions, all API changes must be documented properly in a publicly available changelog."""
API_56_DESCRIPTION = """Version numbering must follow the Semantic Versioning [SemVer] model to prevent breaking changes when releasing new API versions. Versions are formatted using the major.minor.patch template. When releasing a new version which contains backwards-incompatible changes, a new major version must be released. Minor and patch releases may only contain backwards compatible changes (e.g. the addition of an endpoint or an optional attribute)."""
API_57_DESCRIPTION = """Since the URI only contains the major version, it's useful to provide the full version number in the response headers for every API call. This information could then be used for logging, debugging or auditing purposes. In cases where an intermediate networking component returns an error response (e.g. a reverse proxy enforcing access policies), the version number may be omitted.
The version number must be returned in an HTTP response header named API-Version (case-insensitive) and should not be prefixed."""

api_03_20200709 = ChoiceItem(
    "api_03", _("API-03 V-09-07-2020: Only apply standard HTTP methods"),
    description=API_03_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-03",
)
api_16_20200709 = ChoiceItem(
    "api_16", _("API-16 V-09-07-2020: Use OpenAPI Specification for documentation"),
    description=API_16_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-16",
)
api_20_20200709 = ChoiceItem(
    "api_20", _("API-20 V-09-07-2020: Include the major version number in the URI"),
    description=API_20_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-20",
)
api_48_20200709 = ChoiceItem(
    "api_48", _("API-48 V-09-07-2020: Leave off trailing slashes from URIs"),
    description=API_48_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-48",
)
api_51_20200709 = ChoiceItem(
    "api_51_20200709", _("API-51 V-09-07-2020: Publish OAS document at a standard location in JSON-format"),
    description=API_51_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-51",
)
# api_53_20200709 = ChoiceItem(
#     "api_53_20200709", _("API-53 V-09-07-2020: Hide irrelevant implementation details"),
#     description=API_53_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-53",
# )
# api_54_20200709 = ChoiceItem(
#     "api_54_20200709", _("API-54 V-09-07-2020: Use plural nouns to name collection resources"),
#     description=API_54_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-54",
# )
# api_55_20200709 = ChoiceItem(
#     "api_55_20200709", _("API-55 V-09-07-2020: Publish a changelog for API changes between versions"),
#     description=API_55_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-55",
# )
api_56_20200709 = ChoiceItem(
    "api_56_20200709", _("API-56 V-09-07-2020: Adhere to the Semantic Versioning model when releasing API changes"),
    description=API_56_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-56",
)
api_57_20200709 = ChoiceItem(
    "api_57_20200709", _("API-57 V-09-07-2020: Return the full version number in a response header"),
    description=API_57_DESCRIPTION, url="https://publicatie.centrumvoorstandaarden.nl/api/adr/#api-57",
)
