from django.contrib import admin

from .models import DesignRuleSession, DesignRuleResult


@admin.register(DesignRuleSession)
class DesignRuleSessionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'api_endpoint')


@admin.register(DesignRuleResult)
class DesignRuleResultAdmin(admin.ModelAdmin):
    list_display = ('design_rule', 'rule_type')
