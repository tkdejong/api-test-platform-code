from django.contrib import admin

from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

from .models import (
    DesignRuleSession, DesignRuleResult, DesignRuleTestSuite,
    DesignRuleTestVersion, DesignRuleTestOption
)


@admin.register(DesignRuleTestSuite)
class DesignRuleTestSuiteAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'api_endpoint')


@admin.register(DesignRuleSession)
class DesignRuleSessionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'test_suite', 'started_at')


@admin.register(DesignRuleResult)
class DesignRuleResultAdmin(admin.ModelAdmin):
    list_display = ('design_rule', 'rule_type')


class DesignRuleTestOptionInlineAdmin(OrderedTabularInline):
    model = DesignRuleTestOption
    fields = ('rule_type', 'order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    extra = 1
    ordering = ('order',)


@admin.register(DesignRuleTestVersion)
class DesignRuleTestVersionAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ('version', 'name', 'is_active')
    inlines = [DesignRuleTestOptionInlineAdmin]


@admin.register(DesignRuleTestOption)
class DesignRuleTestOptionAdmin(admin.ModelAdmin):
    list_display = ('test_version', 'rule_type')
