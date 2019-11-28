import json
import pytz
from datetime import time

from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.urls import reverse_lazy
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.core.exceptions import PermissionDenied
from guardian.mixins import PermissionRequiredMixin

import vng.postman.utils as postman

from ..utils import choices
from ..utils.views import OwnerSingleObject, PDFGenerator
from .forms import (
    CreateServerRunForm, CreateEndpointForm,
    SelectEnvironmentForm, CreateTestScenarioForm,
    TestScenarioUrlFormSet, PostmanTestFormSet,
    TestScenarioUrlUpdateFormSet, PostmanTestUpdateFormSet
)
from .models import (
    API, ServerRun, Endpoint, TestScenarioUrl, TestScenario, PostmanTest,
    PostmanTestResult, ServerHeader, ScheduledTestScenario, Environment
)
from .task import execute_test


class EnvironmentList(LoginRequiredMixin, ListView):

    template_name = 'servervalidation/environment_list.html'
    context_object_name = 'environment_list'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['api'] = API.objects.get(id=self.kwargs['api_id'])
        return data

    def get_queryset(self):
        res_no_last_run = []
        res = []
        runs_for_user = ServerRun.objects.filter(
            test_scenario__api=self.kwargs['api_id'],
            user=self.request.user,
        )
        distinct_combinations = runs_for_user.select_related(
            'test_scenario', 'environment'
        ).order_by('test_scenario__id', 'environment__id').values_list(
            'test_scenario',
            'environment'
        ).distinct('test_scenario', 'environment')
        for test_scenario_id, environment_id in distinct_combinations:
            test_scenario = TestScenario.objects.get(id=test_scenario_id)
            environment = Environment.objects.get(id=environment_id)

            last_run = environment.last_run
            if last_run:
                res.append((test_scenario, environment, last_run))
            else:
                last_started_at = environment.last_started_at
                res_no_last_run.append((test_scenario, environment, last_started_at))

        # For all the environment that haven't had a stopped run yet, order
        # them by the last started run and display them before the environments
        # with stopped runs
        res_no_last_run.sort(key=lambda x: x[2], reverse=True)
        res_no_last_run = [(scenario, env, None) for scenario, env, _ in res_no_last_run]
        res.sort(key=lambda x: x[2], reverse=True)
        return res_no_last_run + res


class ServerRunList(ListView):

    template_name = 'servervalidation/server-run_list.html'
    context_object_name = 'server_run_list'
    paginate_by = 10
    model = ServerRun

    def get_queryset(self):
        return self.model.objects.filter(
            test_scenario__uuid=self.kwargs['scenario_uuid'],
            environment__uuid=self.kwargs['env_uuid'],
        ).order_by('-stopped', '-started')

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)

        data['test_scenario'] = get_object_or_404(TestScenario, uuid=self.kwargs['scenario_uuid'])
        data['environment'] = get_object_or_404(Environment, uuid=self.kwargs['env_uuid'])
        data['schedule_time'] = time(hour=0, minute=0)

        data['api'] = data['test_scenario'].api

        data['choices'] = dict(choices.StatusWithScheduledChoices.choices)
        data['choices']['error_deploy'] = choices.StatusChoices.error_deploy
        for sr in data['server_run_list']:
            sr.success = sr.get_execution_result()
        return data

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)


class ServerRunForm(CreateView):

    template_name = 'servervalidation/server-run-form.html'
    form_class = CreateServerRunForm

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['api'] = API.objects.get(id=self.kwargs['api_id'])
        return data

    def form_valid(self, form):
        ts_id = form.instance.test_scenario.id
        self.request.session['supplier_name'] = form.instance.supplier_name
        self.request.session['software_product'] = form.instance.software_product
        self.request.session['product_role'] = form.instance.product_role
        self.request.session['software_version'] = form.instance.software_version
        return redirect(reverse('server_run:server-run_select_environment', kwargs={
            "api_id": self.kwargs['api_id'],
            "test_id": ts_id
        }))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'api_id': self.kwargs['api_id']})
        return kwargs


class SelectEnvironment(LoginRequiredMixin, CreateView):

    template_name = 'servervalidation/server-run_select_environment.html'
    form_class = SelectEnvironmentForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        test_scenario = TestScenario.objects.get(id=self.kwargs['test_id'])
        envs = test_scenario.environment_set.filter(user=self.request.user)
        data['form'] = SelectEnvironmentForm(envs=envs)
        data['api'] = test_scenario.api
        data['test_scenario'] = test_scenario
        return data

    def post(self, request, *args, **kwargs):
        test_scenario = TestScenario.objects.get(id=self.kwargs['test_id'])
        envs = test_scenario.environment_set.all()
        form = self.form_class(
            request.POST, envs=envs, test_scenario=test_scenario,
            user=self.request.user
        )
        if form.is_valid():
            new_env_name = request.POST.get('create_env')
            if new_env_name:
                env = Environment.objects.create(test_scenario=test_scenario, name=new_env_name, user=self.request.user)
                return redirect(reverse('server_run:endpoints_create', kwargs={
                    "api_id": env.test_scenario.api.id,
                    "test_id": env.test_scenario.id,
                    "env_id": env.id
                }))
            else:
                env_id = request.POST.get('environment')
                env = Environment.objects.get(id=env_id)
                self.fetch_server()
                self.create_server_run(env)
                return redirect(reverse('server_run:server-run_list', kwargs={
                    'api_id': test_scenario.api.id,
                    'scenario_uuid': test_scenario.uuid,
                    'env_uuid': env.uuid
                }))
        else:
            return render(request, self.template_name, {'form': form})

    def fetch_server(self, scheduled=None):
        ts = get_object_or_404(TestScenario, pk=self.kwargs['test_id'])
        self.server = ServerRun(
            user=self.request.user,
            test_scenario=ts,
            # scheduled=self.request.session.get('server_run_scheduled', False),
            scheduled_scenario=scheduled,
            supplier_name=self.request.session.get('supplier_name', ''),
            software_product=self.request.session.get('software_product', ''),
            software_version=self.request.session.get('software_version', ''),
            product_role=self.request.session.get('product_role', '')
        )

    def create_server_run(self, env):
        self.server.environment = env
        if self.server.scheduled_scenario:
            self.server.status = choices.StatusWithScheduledChoices.scheduled
        else:
            self.server.status = choices.StatusWithScheduledChoices.running
        self.server.save()

        if not self.server.scheduled_scenario:
            execute_test.delay(self.server.pk)

class CreateEndpoint(LoginRequiredMixin, CreateView):

    template_name = 'servervalidation/endpoints_create.html'
    form_class = CreateEndpointForm

    def get_success_url(self):
        return reverse('server_run:server-run_list', kwargs={
            'api_id': self.ts.api.id,
            'scenario_uuid': self.ts.uuid,
            'env_uuid': self.env.uuid
        })

    def fetch_server(self):
        self.env = get_object_or_404(Environment, pk=self.kwargs['env_id'])
        self.ts = get_object_or_404(TestScenario, pk=self.kwargs['test_id'])
        self.server = ServerRun(
            user=self.request.user,
            environment=self.env,
            test_scenario=self.ts,
            supplier_name=self.request.session.get('supplier_name', ''),
            software_product=self.request.session.get('software_product', ''),
            software_version=self.request.session.get('software_version', ''),
            product_role=self.request.session.get('product_role', '')
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        pre_form = data['form']

        self.fetch_server()

        data['ts'] = self.ts
        data['test_scenario'] = TestScenarioUrl.objects.filter(test_scenario=self.ts)
        data['environment'] = self.env
        url_vars = TestScenarioUrl.objects.filter(
            test_scenario=self.ts,
            url=True
        )
        text_vars = TestScenarioUrl.objects.filter(
            test_scenario=self.ts,
            url=False
        )
        data['form'] = CreateEndpointForm(
            url_vars=url_vars,
            text_vars=text_vars,
            url_placeholders=[url.placeholder for url in url_vars],
            text_placeholders=[var.placeholder for var in text_vars]
        )
        if self.ts.jwt_enabled():
            data['form'].add_text_area(['Client ID', 'Secret'])
        elif self.ts.custom_header():
            data['form'].add_text_area(['Authorization header'])
        else:
            pass
        for k, v in pre_form.errors.items():
            data['form'].errors[k] = v
        return data

    def post(self, request, *args, **kwargs):
        data = request.POST

        self.fetch_server()

        testscenariourls = TestScenarioUrl.objects.filter(test_scenario=self.ts)
        tsu_names = [url.name for url in testscenariourls]
        for key, value in data.items():
            if key in tsu_names:
                tsu = testscenariourls.get(name=key)
                Endpoint.objects.create(url=value.strip(), environment=self.env, test_scenario_url=tsu)

        if self.ts.jwt_enabled():
            self.server.client_id = data['Client ID'].strip()
            self.server.secret = data['Secret'].strip()
        elif self.ts.custom_header():
            ServerHeader(environment=self.env, header_key='Authorization', header_value=data['Authorization header'].strip()).save()
        self.server.save()

        if self.server.scheduled:
            self.server.status = choices.StatusWithScheduledChoices.scheduled
        else:
            self.server.status = choices.StatusWithScheduledChoices.running
        self.server.save()

        if not self.server.scheduled:
            execute_test.delay(self.server.pk)

        return HttpResponseRedirect(self.get_success_url())


class ServerRunOutput(OwnerSingleObject, DetailView):

    model = ServerRun
    template_name = 'servervalidation/server-run_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        server_run = context['object']
        ptr = PostmanTestResult.objects.filter(server_run=server_run)
        context["postman_result"] = ptr
        return context


class ServerRunOutputUpdate(UpdateView):

    model = ServerRun
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    fields = [
        'supplier_name',
        'software_product',
        'software_version',
        'product_role',
    ]
    template_name = 'servervalidation/server-run_update.html'

    def get_success_url(self):
        return reverse_lazy(
            'server_run:server-run_detail',
            kwargs={'api_id': self.kwargs['api_id'], 'uuid': self.object.uuid}
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        server_run = context['object']
        ptr = PostmanTestResult.objects.filter(server_run=server_run)
        context["postman_result"] = ptr
        context["update_info"] = False
        return context

    def get_object(self, queryset=None):
        res = super().get_object(queryset=queryset)
        if res.user != self.request.user:
            raise PermissionDenied()
        return res


class ServerRunOutputUuid(DetailView):

    model = ServerRun
    template_name = 'servervalidation/server-run_detail.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self):
        return reverse_lazy(
            'server_run:server-run_detail',
            kwargs={'uuid': self.object.uuid}
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        server_run = context['object']

        # Construct the URL of the changing badge
        changing_badge_url = '{}://{}{}'.format(
            self.request.scheme,
            self.request.get_host(),
            reverse('apiv1server:latest-badge', kwargs={'uuid': server_run.environment.uuid})
        )
        context['changing_badge_url'] = changing_badge_url
        context['api_id'] = server_run.test_scenario.api.id
        ptr = PostmanTestResult.objects.filter(server_run=server_run)
        context["postman_result"] = ptr
        context["update_info"] = True
        return context


class TriggerServerRun(OwnerSingleObject, View):

    model = Environment
    pk_name = 'uuid'
    slug_pk_name = 'uuid'

    def get(self, request, *args, **kwargs):
        environment = self.get_object()
        server = ServerRun.objects.create(
            test_scenario=environment.test_scenario,
            environment=environment,
            user=environment.user
        )
        execute_test.delay(server.pk, email=False)
        return redirect(reverse('server_run:server-run_list', kwargs={
            'api_id': environment.test_scenario.api.id,
            'scenario_uuid': environment.test_scenario.uuid,
            'env_uuid': environment.uuid
        }))


class ScheduleActivate(OwnerSingleObject, View):

    model = Environment
    pk_name = 'uuid'
    slug_pk_name = 'uuid'

    def get(self, request, *args, **kwargs):
        environment = self.get_object()
        scheduled = environment.scheduledtestscenario
        scheduled.active = not scheduled.active
        scheduled.save()
        return redirect(reverse('server_run:server-run_list', kwargs={
            'api_id': environment.test_scenario.api.id,
            'scenario_uuid': environment.test_scenario.uuid,
            'env_uuid': environment.uuid
        }))


class StopServer(OwnerSingleObject, View):

    model = ServerRun
    pk_name = 'server_id'

    def post(self, request, *args, **kwargs):
        server = self.get_object()
        server.stopped = timezone.now()
        server.status = choices.StatusWithScheduledChoices.stopped
        server.save()
        return redirect(reverse('server_run:server-run_list', kwargs={
            'api_id': server.test_scenario.api.id,
            'scenario_uuid': server.test_scenario.uuid,
            'env_uuid': server.environment.uuid
        }))


class ServerRunLogView(DetailView):

    model = ServerRun
    template_name = 'servervalidation/server-run_log.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user == self.object.user or self.object.test_scenario.public_logs:
            return HttpResponse(content=self.object.postmantestresult_set.get(pk=kwargs['test_result_pk']).log)
        else:
            raise PermissionDenied


class ServerRunLogJsonView(DetailView):

    model = ServerRun
    template_name = 'servervalidation/server-run_log_json.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        test_result_pk = self.kwargs.get('test_result_pk')
        test_result = self.object.postmantestresult_set.get(pk=test_result_pk)
        context['postman_test_result'] = test_result
        if self.request.user == test_result.server_run.user or test_result.server_run.test_scenario.public_logs:
            return context
        else:
            raise PermissionDenied


class ServerRunPdfView(PDFGenerator, ServerRunOutputUuid):

    template_name = 'servervalidation/server-run-PDF.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        server_run = context['object']

        ptm = context['postman_result'].get(pk=self.kwargs['test_result_pk'])
        ptm.json = ptm.get_json_obj()
        for calls in ptm.json:
            if 'response' in calls:
                calls['response']['code'] = str(calls['response']['code'])
            else:
                calls['response'] = 'Error occurred call the resource'

        self.filename = 'Server run {} report.pdf'.format(server_run.pk)
        context['error_codes'] = postman.get_error_codes()
        return context


class PostmanDownloadView(View):

    def get(self, request, pk, *args, **kwargs):
        pmt = get_object_or_404(PostmanTest, pk=pk)
        with open(pmt.validation_file.path) as f:
            response = HttpResponse(f, content_type='Application/json')
            response['Content-Length'] = len(response.content)
            response['Content-Disposition'] = 'attachment;filename={}'.format(pmt.filename)
            return response


class TestScenarioDetail(DetailView):

    model = TestScenario
    template_name = 'servervalidation/test_scenario-detail.html'


class CreateSchedule(OwnerSingleObject, View):

    model = Environment
    pk_name = 'uuid'
    slug_pk_name = 'uuid'

    def get(self, request, *args, **kwargs):
        environment = self.get_object()
        ScheduledTestScenario.objects.create(
            environment=environment
        )
        return redirect(reverse('server_run:server-run_list', kwargs={
            'api_id': environment.test_scenario.api.id,
            'scenario_uuid': environment.test_scenario.uuid,
            'env_uuid': environment.uuid
        }))


class LatestRunView(ServerRunOutputUuid):
    model = ServerRun
    template_name = 'servervalidation/server-run_detail.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_object(self):
        server_runs = ServerRun.objects.filter(
            environment__uuid=self.kwargs['env_uuid'],
            test_scenario__uuid=self.kwargs['scenario_uuid']
        ).order_by('-stopped')
        return server_runs.first()


class ObjectPermissionMixin:
    def on_permission_check_fail(self, request, response, obj=None):
        raise PermissionDenied

    def get_permission_object(self):
        return API.objects.get(pk=self.kwargs['api_id'])


class CreateTestScenarioView(ObjectPermissionMixin, PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    template_name = 'servervalidation/test_scenario-form.html'
    form_class = CreateTestScenarioForm
    permission_required = 'servervalidation.create_scenario_for_api'

    def get_success_url(self):
        if hasattr(self, 'test_scenario'):
            return reverse('server_run:testscenario-detail', kwargs={
                'api_id': self.kwargs['api_id'],
                'pk': self.test_scenario.pk
            })
        return reverse('server_run:test-scenario_create_item', kwargs={
            'api_id': self.kwargs['api_id']
        })

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['api'] = API.objects.get(id=self.kwargs['api_id'])

        data['form'] = self.form_class(self.request.POST or None)
        data['variables'] = TestScenarioUrlFormSet(self.request.POST or None)
        data['postman_tests'] = PostmanTestFormSet(self.request.POST or None, self.request.FILES or None)

        # Number of forms to be shown in formset
        extra = self.request.GET.get("extra")
        if extra:
            data['variables'].extra = int(extra)
            data['postman_tests'].extra = int(extra)
        return data

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST

        form = self.form_class(request.POST)
        variable_form = TestScenarioUrlFormSet(request.POST)
        postman_form = PostmanTestFormSet(request.POST, request.FILES)

        if form.is_valid() and variable_form.is_valid() and postman_form.is_valid():
            api = API.objects.get(id=kwargs['api_id'])
            self.test_scenario = TestScenario.objects.create(
                api=api,
                authorization=choices.AuthenticationChoices.no_auth,
                **form.cleaned_data
            )

            variables = []
            for data in variable_form.cleaned_data:
                if data:
                    data["test_scenario"] = self.test_scenario
                    variables.append(TestScenarioUrl(**data))
            TestScenarioUrl.objects.bulk_create(variables)

            postman_tests = []
            for data in postman_form.cleaned_data:
                if data:
                    data["test_scenario"] = self.test_scenario
                    postman_tests.append(PostmanTest(**data))
            PostmanTest.objects.bulk_create(postman_tests)

            return HttpResponseRedirect(self.get_success_url())

        context = {}
        context['api'] = API.objects.get(id=self.kwargs['api_id'])
        context['form'] = form
        context['variables'] = variable_form
        context['postman_tests'] = postman_form
        return render(request, self.template_name, context)


class TestScenarioList(ObjectPermissionMixin, PermissionRequiredMixin, LoginRequiredMixin, ListView):

    template_name = 'servervalidation/test-scenario_list.html'
    context_object_name = 'test-scenario_list'
    paginate_by = 10
    permission_required = 'servervalidation.list_scenario_for_api'

    def get_queryset(self, *args, **kwargs):
        return TestScenario.objects.filter(api__id=self.kwargs['api_id'])

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['api'] = API.objects.get(id=self.kwargs['api_id'])
        return data


class TestScenarioUpdateView(ObjectPermissionMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = TestScenario
    form_class = CreateTestScenarioForm
    pk_url_kwarg = 'scenario_uuid'
    template_name = 'servervalidation/test_scenario-form.html'
    context_object_name = 'testscenario-update'
    permission_required = 'servervalidation.update_scenario_for_api'

    def get_success_url(self):
        return reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.kwargs['api_id']
        })

    def get_object(self):
        return get_object_or_404(TestScenario, uuid=self.kwargs['scenario_uuid'])

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['api'] = API.objects.get(id=self.kwargs['api_id'])

        test_scenario = self.get_object()

        data['form'] = self.form_class(self.request.POST or None, instance=test_scenario)
        data['variables'] = TestScenarioUrlUpdateFormSet(
            self.request.POST or None,
            instance=test_scenario
        )
        data['postman_tests'] = PostmanTestUpdateFormSet(
            self.request.POST or None,
            self.request.FILES or None,
            instance=test_scenario
        )

        # Number of forms to be shown in formset
        extra = self.request.GET.get("extra")
        if extra:
            data['variables'].extra = int(extra)
            data['postman_tests'].extra = int(extra)
        return data

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.POST

        test_scenario = self.get_object()

        form = self.form_class(request.POST, instance=test_scenario)
        variable_form = TestScenarioUrlUpdateFormSet(request.POST, instance=test_scenario)
        postman_form = PostmanTestUpdateFormSet(request.POST, request.FILES, instance=test_scenario)

        if form.is_valid() and variable_form.is_valid() and postman_form.is_valid():
            api = API.objects.get(id=kwargs['api_id'])

            test_scenario = self.get_object()

            for attr, value in form.cleaned_data.items():
                setattr(test_scenario, attr, value)
            test_scenario.save()

            variables = []
            for data in variable_form.cleaned_data:
                if data:
                    if data["DELETE"]:
                        data["id"].delete()
                    elif data["id"] is not None:
                        instance = data.pop("id")
                        data.pop("DELETE")
                        for attr, value in data.items():
                            setattr(instance, attr, value)
                        instance.save()
                    else:
                        data["test_scenario"] = test_scenario
                        data.pop("DELETE")
                        variables.append(TestScenarioUrl(**data))
            TestScenarioUrl.objects.bulk_create(variables)

            postman_tests = []
            for data in postman_form.cleaned_data:
                if data:
                    if data["DELETE"]:
                        data["id"].delete()
                    elif data["id"] is not None:
                        instance = data.pop("id")
                        data.pop("DELETE")
                        for attr, value in data.items():
                            setattr(instance, attr, value)
                        instance.save()
                    else:
                        data["test_scenario"] = test_scenario
                        data.pop("DELETE")
                        postman_tests.append(PostmanTest(**data))
            PostmanTest.objects.bulk_create(postman_tests)

            return HttpResponseRedirect(self.get_success_url())

        context = {}
        context['api'] = API.objects.get(id=self.kwargs['api_id'])
        context['object'] = self.get_object()
        context['form'] = form
        context['variables'] = variable_form
        context['postman_tests'] = postman_form
        return render(request, self.template_name, context)


class TestScenarioDeleteView(ObjectPermissionMixin, PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = TestScenario
    pk_url_kwarg = 'scenario_uuid'
    permission_required = 'servervalidation.delete_scenario_for_api'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('server_run:test-scenario_list', kwargs={
            'api_id': self.kwargs['api_id']
        })

    def get_object(self):
        return get_object_or_404(TestScenario, uuid=self.kwargs['scenario_uuid'])


class UpdateEndpointView(ObjectPermissionMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    template_name = 'servervalidation/endpoints_update.html'
    form_class = CreateEndpointForm
    permission_required = 'servervalidation.update_environment_for_api'

    def get_object(self):
        return Environment.objects.get(id=self.kwargs['env_id'])

    def get_queryset(self, *args, **kwargs):
        return Endpoint.objects.filter(environment_id=self.kwargs['env_id'])

    def get_success_url(self):
        env = self.get_object()
        return reverse('server_run:server-run_list', kwargs={
            'api_id': env.test_scenario.api.id,
            'scenario_uuid': env.test_scenario.uuid,
            'env_uuid': env.uuid
        })

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        pre_form = data['form']

        self.env = self.get_object()
        self.ts = self.env.test_scenario

        data['ts'] = self.ts
        data['test_scenario'] = TestScenarioUrl.objects.filter(test_scenario=self.ts)
        data['environment'] = self.env
        url_vars = TestScenarioUrl.objects.filter(
            test_scenario=self.ts,
            url=True
        )
        text_vars = TestScenarioUrl.objects.filter(
            test_scenario=self.ts,
            url=False
        )
        data['form'] = CreateEndpointForm(
            url_vars=url_vars,
            text_vars=text_vars,
            url_placeholders=Endpoint.objects.filter(environment=self.env, test_scenario_url__in=url_vars).values_list('url', flat=True),
            text_placeholders=Endpoint.objects.filter(environment=self.env, test_scenario_url__in=text_vars).values_list('url', flat=True)
        )
        if self.ts.jwt_enabled():
            data['form'].add_text_area(['Client ID', 'Secret'])
        elif self.ts.custom_header():
            data['form'].add_text_area(['Authorization header'])
        else:
            pass
        for k, v in pre_form.errors.items():
            data['form'].errors[k] = v
        return data

    def post(self, request, *args, **kwargs):
        data = request.POST
        env = self.get_object()
        endpoints = env.endpoint_set.all()
        tsu_names = endpoints.values_list('test_scenario_url__name', flat=True)

        modified = False
        for key, value in data.items():
            if key in tsu_names:
                endpoint = endpoints.get(test_scenario_url__name=key)

                if value.strip() != endpoint.url:
                    endpoint.url = value.strip()
                    endpoint.save()
                    modified = True

        # Delete all historic server runs for this environment
        # if changes were made
        if modified:
            env.serverrun_set.all().delete()

        return HttpResponseRedirect(self.get_success_url())
