import factory

from ..choices import DesignRuleChoices
from ..models import DesignRuleTestSuite, DesignRuleSession, DesignRuleResult, DesignRuleTestOption, DesignRuleTestVersion


class DesignRuleTestVersionFactory(factory.django.DjangoModelFactory):
    is_active = True
    name = factory.Faker("word")
    version = factory.Faker("word")

    class Meta:
        model = DesignRuleTestVersion


class DesignRuleTestOptionFactory(factory.django.DjangoModelFactory):
    test_version = factory.SubFactory(DesignRuleTestVersionFactory)
    rule_type = DesignRuleChoices.api_03_20200709

    class Meta:
        model = DesignRuleTestOption


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
