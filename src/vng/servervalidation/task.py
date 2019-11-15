import uuid
from zds_client import ClientAuth
import traceback
import re
import json

from django.core.files import File
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from celery.utils.log import get_task_logger
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from vng.postman.choices import ResultChoices

from ..celery.celery import app
from .models import PostmanTest, PostmanTestResult, Endpoint, ServerRun, ServerHeader, ScheduledTestScenario
from ..utils import choices
from ..utils.newman import NewmanManager
from ..utils.auth import get_jwt


logger = get_task_logger(__name__)


@app.task
def execute_test_scheduled():
    scheduled_scenarios = ScheduledTestScenario.objects.filter(active=True)
    test_results = {user_id: [] for user_id in scheduled_scenarios.values_list('environment__user', flat=True).distinct('environment__user')}

    for schedule in scheduled_scenarios:
        environment = schedule.environment
        server_run = ServerRun.objects.create(
            test_scenario=environment.test_scenario,
            scheduled_scenario=schedule,
            environment=environment,
            user=environment.user,
            status=choices.StatusWithScheduledChoices.running
        )
        execute_test(server_run.pk, scheduled=True)
        failed = server_run.get_execution_result()
        test_results[environment.user.id].append((server_run, failed))

    if test_results:
        send_email_failure(test_results)

def substitute_hidden_vars(server_run, file):
    data = file.read()
    hidden_vars = server_run.endpoint_set.filter(test_scenario_url__hidden=True)
    for hidden in hidden_vars:
        data = re.sub('{}'.format(hidden.url), '{hidden}', data)
    return data


@app.task
def execute_test(server_run_pk, scheduled=False, email=False):
    server_run = ServerRun.objects.get(pk=server_run_pk)
    server_run.status = choices.StatusWithScheduledChoices.running
    endpoints = server_run.environment.endpoint_set.all()

    file_name = str(uuid.uuid4())
    postman_tests = PostmanTest.objects.filter(test_scenario=server_run.test_scenario).order_by('order')

    failure = False
    try:
        for counter, postman_test in enumerate(postman_tests):
            auth_choice = postman_test.test_scenario.authorization
            if auth_choice == choices.AuthenticationChoices.jwt:
                jwt_auth = get_jwt(server_run).credentials()
            server_run.status_exec = 'Running the test {}'.format(postman_test.validation_file)
            server_run.percentage_exec = int(((counter + 1) / (len(postman_tests) + 1)) * 100)
            server_run.save()
            nm = NewmanManager(postman_test.validation_file)

            if auth_choice == choices.AuthenticationChoices.jwt:
                nm.replace_parameters({
                    'BEARER_TOKEN': list(jwt_auth.values())[0].split()[1]
                })
            elif auth_choice == choices.AuthenticationChoices.header:
                se = ServerHeader.objects.filter(server_run=server_run)
                for header in se:
                    nm.replace_parameters({
                        'Authentication': header.header_value
                    })
            elif auth_choice == choices.AuthenticationChoices.no_auth:
                pass
            param = {}
            for ep in endpoints:
                param[ep.test_scenario_url.name] = ep.url
            nm.replace_parameters(param)
            file_html, file_json = nm.execute_test()
            ptr = PostmanTestResult(
                postman_test=postman_test,
                server_run=server_run
            )
            data = substitute_hidden_vars(server_run, file_html)
            data_json = substitute_hidden_vars(server_run, file_json)

            with open(file_html.name, 'w') as f:
                f.write(data)

            with open(file_json.name, 'w') as f:
                json.dump(json.loads(data_json), f, indent=4)

            ptr.log.save(file_name, File(open(file_html.name)))
            ptr.save_json(file_name, File(open(file_json.name)))
            ptr.status = ptr.get_outcome_json()
            ptr.save()
            failure = failure or (ptr.status == ResultChoices.failed)

        server_run.status_exec = 'Completed'
    except Exception as e:
        logger.warning(e)
        server_run.status = choices.StatusChoices.error_deploy
        server_run.status_exec = traceback.format_exc()

    server_run.percentage_exec = 100
    if server_run.status != choices.StatusChoices.error_deploy:
        server_run.status = choices.StatusWithScheduledChoices.stopped
    server_run.stopped = timezone.now()

    if email:
        send_email_failure({server_run.user.id: [(server_run, failure)]})
    server_run.save()
    return failure


def send_email_failure(test_results):
    from django.contrib.sites.models import Site
    domain = Site.objects.get_current().domain

    for user_id, result_list in test_results.items():
        msg_html = render_to_string('servervalidation/scheduled_test_email.html', {
            'successful': [(run, failed) for run, failed in result_list if failed is False],
            'failure': [(run, failed) for run, failed in result_list if failed is True],
            'error': [(run, failed) for run, failed in result_list if failed is None],
            'domain': domain
        })

        user = get_user_model().objects.get(id=user_id)

        send_mail(
            _('Results of scheduled tests'),
            msg_html,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=msg_html
        )
