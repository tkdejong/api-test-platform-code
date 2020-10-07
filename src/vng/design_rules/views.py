from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView

from vng.servervalidation.models import API

from .forms import DesignRuleTestSuiteForm
from .models import DesignRuleTestSuite, DesignRuleSession


class DesignRulesListView(LoginRequiredMixin, ListView):
    model = DesignRuleTestSuite
    template_name = "design_rules/list.html"


class DesignRulesCreateView(CreateView):
    model = DesignRuleTestSuite
    template_name = "design_rules/create.html"
    form_class = DesignRuleTestSuiteForm

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.start_session()
        return response

    def get_success_url(self) -> str:
        return reverse("design_rules:list")


class DesignRulesDetailView(DetailView):
    template_name = "design_rules/detail.html"
    model = DesignRuleTestSuite
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'


class DesignRuleSessionCreateView(SingleObjectMixin, RedirectView):
    model = DesignRuleTestSuite
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.start_session()
        return super().get(*args, **kwargs)

    def get_redirect_url(self, **kwargs) -> str:
        return reverse("design_rules:detail", kwargs={"uuid": self.object.uuid})


class DesignRuleSessionDetailView(DetailView):
    template_name = "design_rules/sessions/detail.html"
    model = DesignRuleSession
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'
