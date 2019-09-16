from django.db.models import Q
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from vng.servervalidation.models import ServerRun, TestScenario
from vng.testsession.models import (
    ScenarioCase, Session, SessionLog, ExposedUrl,
    TestSession, Report, SessionType, VNGEndpoint
)
from vng.utils import choices

class Dashboard(LoginRequiredMixin, TemplateView):

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
