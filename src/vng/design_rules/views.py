from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import InvalidPage, Paginator
from django.http.response import Http404
from django.urls.base import reverse
from django.utils.translation import ugettext_lazy as _
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
    paginate_by = 20


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        test_suite = self.get_object()
        paginator, page, queryset, is_paginated = self.paginate_queryset(test_suite.sessions.all(), 10)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['is_paginated'] = is_paginated
        context['object_list'] = queryset
        return context

    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset, if needed."""
        paginator = self.get_paginator(
            queryset, page_size, orphans=0,
            allow_empty_first_page=True)
        page_kwarg = 'page'
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                'page_number': page_number,
                'message': str(e)
            })

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        """Return an instance of the paginator for this view."""
        return Paginator(
            queryset, per_page, orphans=orphans,
            allow_empty_first_page=allow_empty_first_page, **kwargs)


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
