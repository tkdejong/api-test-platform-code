import logging
import json
from collections import defaultdict
import os
import uuid
from urllib.parse import urlparse

from django.conf import settings

from ..utils.commands import run_command_with_shell

logger = logging.getLogger(__name__)


class DidNotRunException(Exception):
    pass


class NewmanManager:
    REPORT_FOLDER = settings.MEDIA_ROOT + '/newman'
    newman_path = os.path.join(settings.BASE_DIR, 'node_modules', 'newman', 'bin', 'newman.js')
    RUN_REPORT = ('NODE_OPTIONS="--max-old-space-size=2048" '
                       '{} run --reporters "htmlextra,json" {} '
                       '--timeout-request 50000 '
                       '--reporter-htmlextra-darkTheme '
                       '--reporter-htmlextra-testPaging '
                       '--reporter-htmlextra-title '
                       '--reporter-htmlextra-logs '
                       '--reporter-htmlextra-export ' + REPORT_FOLDER + '/{}.html '
                       '--reporter-json-export ' + REPORT_FOLDER + '/{}.json {}')
    ENV_VAR_SYNTAX = ' --env-var {}={} '
    TOKEN = 'TOKEN'

    def __init__(self, file, api_endpoint=None):
        self.file = file
        self.file_to_be_discarted = []
        self.global_vars = ''
        self.api_endpoint = api_endpoint
        if not os.path.exists(self.REPORT_FOLDER):
            os.makedirs(self.REPORT_FOLDER)

    def __del__(self):
        for file in self.file_to_be_discarted:
            full_path = os.path.realpath(file.name)
            logger.debug('Deleteing file {}'.format(full_path))
            os.remove(full_path)

    def run_command(self, command, *args):
        command = command.format(*args, self.global_vars)
        return run_command_with_shell(command)

    def replace_parameters(self, _dict):
        for k, v in _dict.items():
            self.global_vars += self.ENV_VAR_SYNTAX.format(k, v)

    def execute_test(self):
        self.file_path = self.file.path
        filename = str(uuid.uuid4())
        output, error = self.run_command(
            self.RUN_REPORT, self.newman_path, self.file_path, filename, filename
        )
        if error:
            assert False, error
            logger.exception(error)
            raise DidNotRunException()
        f_html = open('{}/{}.html'.format(self.REPORT_FOLDER, filename))
        f_json = open('{}/{}.json'.format(self.REPORT_FOLDER, filename))
        self.file_to_be_discarted.append(f_html)
        self.file_to_be_discarted.append(f_json)
        return f_html, f_json


class OpenAPIConverter:
    converter_path = os.path.join(settings.BASE_DIR, 'node_modules', 'openapi-to-postmanv2', 'bin', 'openapi2postmanv2.js')
    base_command = converter_path + " -s {} -o {}"

    def __init__(self, *args, **kwargs):
        from drf_yasg import openapi
        self.openapi_types = [
            openapi.TYPE_ARRAY, openapi.TYPE_BOOLEAN, openapi.TYPE_FILE, openapi.TYPE_INTEGER,
            openapi.TYPE_NUMBER, openapi.TYPE_OBJECT, openapi.TYPE_STRING
        ]
        self.openapi_format = [
            openapi.FORMAT_BASE64, openapi.FORMAT_BINARY, openapi.FORMAT_DATE,
            openapi.FORMAT_DATETIME, openapi.FORMAT_DECIMAL, openapi.FORMAT_DOUBLE,
            openapi.FORMAT_EMAIL, openapi.FORMAT_FLOAT, openapi.FORMAT_INT32,
            openapi.FORMAT_INT64, openapi.FORMAT_IPV4, openapi.FORMAT_IPV6,
            openapi.FORMAT_PASSWORD, openapi.FORMAT_SLUG, openapi.FORMAT_URI,
            openapi.FORMAT_UUID
        ]

    def generate_collection(self, api_spec, output_file):
        command = self.base_command.format(api_spec, output_file)
        self.file = output_file
        return run_command_with_shell(command)

    def process_collection(self):
        assert hasattr(self, "file"), "An API spec must be converted first"
        with open(self.file, "r") as f:
            collection = json.load(f)
            self.modify_item(collection)
        with open(self.file, "w") as f:
            json.dump(collection, f)


    # TODO fix ordering of requests (create before retrieve, etc)
    # generate valid body/querystring values
    def modify_item(self, item):
        if isinstance(item, list):
            for i in item:
                self.modify_item(i)
        elif isinstance(item, dict):
            if "item" in item:
                self.modify_item(item["item"])
            else:
                item["event"] = generate_testscript(item, self.openapi_types, self.openapi_format)

                # Inherit auth from parent
                item["request"].pop("auth", None)

                # Disable query parameters, must be entered manually
                for param in item["request"]["url"]["query"]:
                    param["disabled"] = True


def generate_testscript(item, openapi_types, openapi_format):
    if "response" in item:
        status_code = item["response"][0]["code"]
    else:
        status_code = {"GET": 200, "POST": 201, "PUT": 200, "PATCH": 200, "DELETE": 204}[item["request"]["method"]]
    event = [
        {
            "listen": "test",
            "script": {
                "id": str(uuid.uuid4()),
                "exec": ["pm.test(\"{} geeft {}\", function() {{\n\tpm.response.to.have.status({});\n}});".format(item['name'], status_code, status_code)]
            },
            "type": "text/javascript"
        }
    ]
    # TODO fix json schema generation
    # if status_code != 204:
    #     infinite_dict = lambda: defaultdict(infinite_dict)
    #     schema = infinite_dict()
    #     if item["response"][0]["body"]:
    #         valid_body = json.loads(item["response"][0]["body"])
    #         generate_schema(schema, valid_body, openapi_types, openapi_format)

    #         validate_body_script = ("pm.test(\"{} heeft valide body\", function() {{\n"
    #                             "\tconst Ajv = require('ajv');\n"
    #                             "\tvar ajv = new Ajv({{logger: console}});\n"
    #                             "\tvar schema = {};\n"
    #                             "\tpm.expect(ajv.validate(schema, pm.response.json())).to.be.true;\n"
    #                             "}});").format(item['name'], json.dumps(schema))
    #         event[0]["script"]["exec"].append(validate_body_script)
    return event

def generate_schema(schema, body, openapi_types, openapi_format):
    if isinstance(body, dict):
        for key, value in body.items():
            if isinstance(value, list):
                for i in value:
                    generate_schema(schema["properties"][key]["items"], i, openapi_types, openapi_format)
            elif isinstance(value, dict):
                generate_schema(schema["properties"][key], value, openapi_types, openapi_format)
            elif isinstance(value, str):
                value = value.replace('<', '').replace('>', '')
                # The openapi2postman converter does not show the type if a format is
                # given https://github.com/postmanlabs/openapi-to-postman/issues/139
                if value in openapi_types:
                    schema["properties"][key]["type"] = value
                if value in openapi_format:
                    schema["properties"][key]["format"] = value
