import logging
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
