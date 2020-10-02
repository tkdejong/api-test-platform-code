from django.contrib import admin

from .models import DesignRuleSession, DesignRuleResult, DesignRuleTestSuite


@admin.register(DesignRuleTestSuite)
class DesignRuleTestSuiteAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'api_endpoint')


@admin.register(DesignRuleSession)
class DesignRuleSessionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'test_suite', 'started_at')


@admin.register(DesignRuleResult)
class DesignRuleResultAdmin(admin.ModelAdmin):
    list_display = ('design_rule', 'rule_type')
