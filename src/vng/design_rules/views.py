from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from vng.servervalidation.models import API

from .forms import DesignRulesSessionForm
from .models import DesignRuleSession


class DesignRulesListView(LoginRequiredMixin, ListView):
    model = DesignRuleSession
    template_name = "design_rules/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['api'] = API.objects.get(id=self.kwargs['api_id'])
        # sessions_related = [(session, *session.get_report_stats()) for session in context['object_list']]
        # context['object_list'] = sessions_related
        return context


class DesignRulesCreateView(CreateView):
    model = DesignRuleSession
    template_name = "design_rules/create.html"
    form_class = DesignRulesSessionForm

    def get_api(self):
        return API.objects.get(id=self.kwargs['api_id'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['api'] = self.get_api()
        # sessions_related = [(session, *session.get_report_stats()) for session in context['object_list']]
        # context['object_list'] = sessions_related
        return context

    def get_success_url(self) -> str:
        return reverse("design_rules:list", kwargs={"api_id": self.kwargs['api_id']})


class DesignRulesDetailView(DetailView):
    template_name = "design_rules/detail.html"
    model = DesignRuleSession
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'

    def get_api(self):
        return API.objects.get(id=self.kwargs['api_id'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['api'] = self.get_api()
        return context
