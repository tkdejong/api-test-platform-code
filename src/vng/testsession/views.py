import json
import logging


from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View

from vng.accounts.models import User
from vng.servervalidation.models import ServerRun, TestScenario

from .models import (
    ScenarioCase, Session, SessionLog, ExposedUrl,
    TestSession, Report, SessionType, VNGEndpoint
)

from .task import bootstrap_session, stop_session
from .forms import SessionForm
from ..utils import choices
from ..utils.views import OwnerSingleObject, PDFGenerator


logger = logging.getLogger(__name__)


class SessionListView(LoginRequiredMixin, ListView):

    template_name = 'testsession/sessions-list.html'
    context_object_name = 'sessions_list'
    paginate_by = 10
    model = Session

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        _choices = dict(choices.StatusChoices.choices)
        _choices['error_deploy'] = choices.StatusChoices.error_deploy
        context.update({
            'choices': _choices,
        })
        sessions_related = [(session, *session.get_report_stats()) for session in context['object_list']]
        context['object_list'] = sessions_related
        return context

    def get_queryset(self):
        '''
        Group all the exposed url by the session in order to display later all related url together
        '''
        return Session.objects.filter(user=self.request.user).order_by('-started')


class Dashboard(TemplateView):

    template_name = 'testsession/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['sessions_active'] = (
            Session.objects
            .filter(Q(status=choices.StatusChoices.running) | Q(status=choices.StatusChoices.starting))
            .filter(user=self.request.user)
            .count()
        )
        context['sessions_active_docker'] = (
            Session.objects
            .filter(Q(status=choices.StatusChoices.running) | Q(status=choices.StatusChoices.starting))
            .filter(session_type__vngendpoint__docker_image__isnull=False)
            .filter(user=self.request.user)
            .count()
        )
        context['sessions_active_hosted'] = (
            Session.objects
            .filter(Q(status=choices.StatusChoices.running) | Q(status=choices.StatusChoices.starting))
            .filter(session_type__vngendpoint__docker_image__isnull=True)
            .filter(user=self.request.user)
            .count()
        )
        context['servers_scheduled'] = ServerRun.objects.filter(user=self.request.user) \
            .filter(scheduled=True) \
            .filter(
                Q(status=choices.StatusWithScheduledChoices.running)
                | Q(status=choices.StatusWithScheduledChoices.starting)
                | Q(status=choices.StatusWithScheduledChoices.scheduled)) \
            .order_by('-started') \
            .filter(user=self.request.user) \
            .count()
        context['server_running'] = ServerRun.objects.filter(user=self.request.user) \
            .filter(scheduled=False) \
            .filter(
                Q(status=choices.StatusWithScheduledChoices.running)
                | Q(status=choices.StatusWithScheduledChoices.starting)) \
            .order_by('-started') \
            .filter(user=self.request.user) \
            .count()
        context['session_types'] = SessionType.objects.all().count()
        context['test_scenario'] = TestScenario.objects.all().count()

        return context


class SessionFormView(FormView):

    template_name = 'testsession/session-form.html'
    form_class = SessionForm

    def get_success_url(self):
        return reverse('testsession:sessions')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.started = timezone.now()
        form.instance.status = choices.StatusChoices.starting
        form.instance.assign_name(self.request.user.id)
        form.instance.name = Session.assign_name(self.request.user.id)
        session = form.save()
        bootstrap_session.delay(session.pk)
        return HttpResponseRedirect(self.get_success_url())


class SessionLogDetailView(OwnerSingleObject):

    template_name = 'testsession/session-log-detail.html'
    context_object_name = 'log_list'
    model = SessionLog
    pk_name = 'log_uuid'
    slug_pk_name = 'uuid'
    user_field = 'session__user'


class SessionLogView(ListView):

    template_name = 'testsession/session-log.html'
    context_object_name = 'log_list'
    paginate_by = 200

    def get_queryset(self):
        return SessionLog.objects.filter(session__uuid=self.kwargs['uuid']).order_by('date')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        session = get_object_or_404(Session, uuid=self.kwargs['uuid'])
        stats = session.get_report_stats()
        _choices = dict(choices.StatusChoices.choices)
        _choices['error_deploy'] = choices.StatusChoices.error_deploy
        context.update({
            'choices': _choices,
        })
        context.update({
            'session': session,
            'success': stats[0],
            'failed': stats[1],
            'not_called': stats[2],
            'total': sum(stats)
        })
        return context


class SessionLogUpdateView(UpdateView):

    template_name = 'testsession/session-update.html'
    context_object_name = 'session'
    model = Session
    slug_field = 'pk'
    slug_url_kwarg = 'session_id'
    fields = [
        'supplier_name',
        'software_product',
        'product_role',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = context['session']
        stats = session.get_report_stats()

        context.update({
            'session': session,
            'success': stats[0],
            'failed': stats[1],
            'not_called': stats[2],
            'total': sum(stats),
        })
        return context

    def get_success_url(self):
        return reverse_lazy(
            'testsession:session_log',
            kwargs={'uuid': self.object.uuid}
        )

    def get_object(self, queryset=None):
        res = super().get_object(queryset=queryset)
        if res.user != self.request.user:
            raise PermissionDenied()
        return res


class StopSession(OwnerSingleObject, View):

    model = Session
    pk_name = 'session_id'

    def post(self, request, *args, **kwargs):
        session = self.get_object()
        if session.status == choices.StatusChoices.stopped or session.status == choices.StatusChoices.shutting_down:
            return HttpResponseRedirect(reverse('testsession:sessions'))

        session.status = choices.StatusChoices.shutting_down
        session.save()
        stop_session.delay(session.pk)
        return HttpResponseRedirect(reverse('testsession:sessions'))


class SessionReport(DetailView):

    model = ScenarioCase
    template_name = 'testsession/session-report.html'

    def get_object(self):
        self.session = get_object_or_404(Session, uuid=self.kwargs['uuid'])
        return self.session

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = list(Report.objects.filter(session_log__session=self.session))
        report_ordered = []
        for case in context['session'].session_type.scenario_cases:
            is_in = False
            for rp in report:
                if rp.scenario_case == case:
                    report_ordered.append(rp)
                    is_in = True
                    break
            if not is_in:
                report_ordered.append(Report(scenario_case=case, result=choices.HTTPCallChoices.not_called))

        context.update({
            'session': self.session,
            'object_list': report_ordered,
            'session_type': self.session.session_type,
        })
        return context


class SessionReportPdf(PDFGenerator, SessionReport):

    template_name = 'testsession/session-report-PDF.html'


class SessionTestReport(OwnerSingleObject):

    model = TestSession
    template_name = 'testsession/session-test-report.html'
    pk_name = 'uuid'
    user_field = 'exposedurl__session__user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = ExposedUrl.objects.filter(test_session=self.object).first().session
        context.update({
            'session': session
        })
        return context


class SessionTestReportPDF(PDFGenerator, SessionTestReport):

    template_name = 'testsession/session-test-report-PDF.html'

    def parse_json(self, obj):
        parsed = json.loads(obj)
        for run in parsed['run']['executions']:
            url = run['request']['url']
            if 'protocol' in url:
                new_url = url['protocol'] + '://'
            else:
                new_url = 'https://'
            for k in run['request']['header']:
                if k['key'] == 'Host':
                    new_url += k['value']
            new_url += '/'
            if 'path' in url:
                for p in url['path']:
                    new_url += p + '/'

            run['request']['url'] = new_url

        return parsed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = kwargs['object']

        context.update({
            'report': self.parse_json(session.json_result)
        })
        return context


class PostmanDownloadView(View):

    def get(self, request, pk, *args, **kwargs):
        eu = get_object_or_404(ExposedUrl, pk=pk)
        with open(eu.vng_endpoint.test_file.path) as f:
            response = HttpResponse(f, content_type='Application/json')
            response['Content-Length'] = len(response.content)
            response['Content-Disposition'] = 'attachment;filename=test{}.json'.format(eu.vng_endpoint.name)
            return response


class SessionTypeDetail(DetailView):

    model = SessionType
    template_name = 'testsession/session_type-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scenario_cases'] = context['sessiontype'].scenario_cases
        return context
