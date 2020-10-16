import factory

from ..models import DesignRuleTestSuite, DesignRuleSession, DesignRuleResult


class DesignRuleTestSuiteFactory(factory.django.DjangoModelFactory):
    api_endpoint = "https://maykinmedia.nl/"

    class Meta:
        model = DesignRuleTestSuite


class DesignRuleSessionFactory(factory.django.DjangoModelFactory):
    test_suite = factory.SubFactory(DesignRuleTestSuiteFactory)

    class Meta:
        model = DesignRuleSession


class DesignRuleResultFactory(factory.django.DjangoModelFactory):
    design_rule = factory.SubFactory(DesignRuleSessionFactory)

    class Meta:
        model = DesignRuleResult
