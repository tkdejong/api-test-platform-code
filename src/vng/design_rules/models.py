from decimal import Decimal
from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ordered_model.models import OrderedModel

from .choices import DesignRuleChoices
from .tasks.base import run_tests


class DesignRuleTestVersion(models.Model):
    version = models.CharField(default="", max_length=200)
    name = models.CharField(default="", max_length=200)
    url = models.URLField(null=True)
    is_active = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "{} - {}".format(self.version, self.name)


class DesignRuleTestOption(OrderedModel):
    test_version = models.ForeignKey(DesignRuleTestVersion, null=True, on_delete=models.CASCADE, related_name="test_rules")
    rule_type = models.CharField(max_length=50, default="", choices=DesignRuleChoices.choices, blank=True)

    order_with_respect_to = 'test_version'

    class Meta(OrderedModel.Meta):
        pass


class DesignRuleTestSuite(models.Model):
    uuid = models.UUIDField(default=uuid4)
    api_endpoint = models.URLField(unique=True)
    # Optional URL to the OpenAPI specification file.
    # Only necessary if it is not located at the default location relative to the api_endpoint.
    specification_url = models.URLField(blank=True)

    def start_session(self, test_version):
        session = self.sessions.create(test_version=test_version)
        session.start_tests(self.api_endpoint, self.specification_url)
        return session

    def get_latest_session(self):
        if self.sessions.exists():
            return self.sessions.first()
        return None

    def successful(self):
        session = self.get_latest_session()
        if session:
            return session.successful()
        return False

    def percentage_score(self):
        session = self.get_latest_session()
        if session:
            return session.percentage_score
        return Decimal("0.00")


class DesignRuleSession(models.Model):
    uuid = models.UUIDField(default=uuid4)
    test_suite = models.ForeignKey(DesignRuleTestSuite, on_delete=models.CASCADE, related_name="sessions", null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    json_result = models.TextField(blank=True, null=True, default=None, help_text=_("This is the downloaded api spec"))
    percentage_score = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    test_version = models.ForeignKey(DesignRuleTestVersion, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-started_at", )

    def start_tests(self, api_endpoint, specification_url=""):
        run_tests(self, api_endpoint, specification_url)

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
    errors = ArrayField(
        models.CharField(max_length=500, blank=True), null=True, blank=True
    )
    warnings = ArrayField(
        models.CharField(max_length=500, blank=True), null=True, blank=True
    )

    class Meta:
        ordering = ('design_rule', )

    def get_errors(self):
        if self.errors:
            return "\n".join(self.errors)
        return ""

    def get_warnings(self):
        if self.warnings:
            return "\n".join(self.warnings)
        return ""

    def get_url(self):
        choice = DesignRuleChoices.get_choice(self.rule_type)
        return choice.url

    def get_description(self):
        choice = DesignRuleChoices.get_choice(self.rule_type)
        return choice.description
