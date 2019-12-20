import json

from django_webtest import WebTest
from django.urls import reverse
from django.utils.translation import ugettext as _

from vng.testsession.tests.factories import UserFactory


class PostmanCollectionGeneratorTests(WebTest):

    def setUp(self):
        self.user = UserFactory.create()

    def test_generate_collection_from_oas(self):
        response = self.app.get(reverse("server_run:collection_generator"), user=self.user)
        form = response.forms[1]

        form['oas_file'] = ["src/vng/servervalidation/tests/data/test_oas.yaml"]
        form['filename'] = "test"
        response = form.submit()

        self.assertEqual(response.content_disposition, "attachment;filename=test.json")

        collection = json.loads(response.content)
        self.assertIn("item", collection)

        event = collection["item"][0]["item"][0]["event"][0]

        self.assertIn("script", event)

        # Two testscripts, one for status code and one for body schema
        self.assertEqual(len(event["script"]["exec"]), 2)
        self.assertEqual(event["script"]["exec"][0], 'pm.test("Alle BESLUITen opvragen. geeft 200", \
function() {\n\tpm.response.to.have.status(200);\n});')
        self.assertEqual(event["script"]["exec"][1], 'pm.test("Alle BESLUITen opvragen. \
heeft valide body", function() {\n\tconst Ajv = require(\'ajv\');\n\tvar ajv = \
new Ajv({logger: console});\n\tvar schema = {"properties": {"count": {"type": "integer"}, \
"results": {"items": {"properties": {"verantwoordelijkeOrganisatie": {"type": "string"}, "besluittype": \
{"format": "uri"}, "datum": {"format": "date"}, "ingangsdatum": {"format": "date"}, "url": \
{"format": "uri"}, "identificatie": {"type": "string"}, "zaak": {"format": "uri"}, \
"toelichting": {"type": "string"}, "bestuursorgaan": {"type": "string"}, "vervaldatum": \
{"format": "date"}, "vervalreden": {"type": "string"}, "vervalredenWeergave": \
{"type": "string"}, "publicatiedatum": {"format": "date"}, "verzenddatum": \
{"format": "date"}, "uiterlijkeReactiedatum": {"format": "date"}}}}, "next": \
{"format": "uri"}, "previous": {"format": "uri"}}};\n\tpm.expect(ajv.validate\
(schema, pm.response.json())).to.be.true;\n});')

    def test_generate_collection_from_invalid_oas(self):
        response = self.app.get(reverse("server_run:collection_generator"), user=self.user)
        form = response.forms[1]

        form['oas_file'] = ["src/vng/servervalidation/tests/data/invalid_oas.yaml"]
        form['filename'] = "test"
        response = form.submit()

        self.assertIn(_(
            "openapi2postman was not able to convert the uploaded file, "
            "please upload a valid OpenAPI specification"
        ), response.text)

    def test_generator_page_not_accessible_without_login(self):
        response = self.app.get(reverse("server_run:collection_generator"))

        self.assertEqual(response.status_code, 302)
