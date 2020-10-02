from uuid import uuid4

from django.db import models
from django.utils.translation import ugettext_lazy as _

from vng.servervalidation.models import API

from .tasks.base import run_tests

from .choices import DesignRuleChoices


class DesignRuleTestSuite(models.Model):
    uuid = models.UUIDField(default=uuid4)
    api_endpoint = models.URLField()

    def start_session(self):
        session = self.sessions.create()
        session.start_tests(self.api_endpoint)
        return session

    def successful(self):
        if self.sessions.exists():
            return self.sessions.first().successful()
        return False

    def percentage_score(self):
        if self.sessions.exists():
            return self.sessions.first().percentage_score
        return 0


class DesignRuleSession(models.Model):
    uuid = models.UUIDField(default=uuid4)
    test_suite = models.ForeignKey(DesignRuleTestSuite, on_delete=models.CASCADE, related_name="sessions", null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    json_result = models.TextField(blank=True, null=True, default=None, help_text=_("This is the downloaded api spec"))
    percentage_score = models.DecimalField(default=0, decimal_places=2, max_digits=5)

    class Meta:
        ordering = ("-started_at", )

    def start_tests(self, api_endpoint):
        run_tests(self, api_endpoint)

    def successful(self):
        if self.results.exists():
            list_successes = self.results.values_list("success", flat=True)
            return all(list(list_successes))
        return False


class DesignRuleResult(models.Model):
    uuid = models.UUIDField(default=uuid4)
    design_rule = models.ForeignKey(DesignRuleSession, on_delete=models.CASCADE, related_name="results")
    rule_type = models.CharField(max_length=50, default="", choices=DesignRuleChoices.choices)
    success = models.BooleanField(default=False, blank=True)
    errors = models.TextField(default="")

    class Meta:
        ordering = ('design_rule', )
