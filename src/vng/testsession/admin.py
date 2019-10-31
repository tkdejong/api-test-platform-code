from ordered_model.admin import OrderedModelAdmin, OrderedTabularInline, OrderedInlineModelAdminMixin
from django.contrib import admin


import vng.testsession.models as model

from .forms import SessionTypeFormAdmin


class VNGEndpointInline(OrderedTabularInline):
    model = model.VNGEndpoint
    fields = ('url', 'move_up_down_links', 'name', 'path', 'docker_image', 'session_type', 'port', 'test_file', 'scenario_collection',)
    readonly_fields = ('move_up_down_links',)
    extra = 1
    ordering = ('order',)


class ScenarioCaseInline(OrderedTabularInline):
    model = model.ScenarioCase
    fields = ('url', 'description', 'move_up_down_links', 'http_method',)
    readonly_fields = ('move_up_down_links',)
    extra = 1
    ordering = ('order',)


class ScenarioCaseCollectionInline(admin.TabularInline):
    model = model.ScenarioCaseCollection


class ExposedUrlInline(admin.TabularInline):
    model = model.ExposedUrl


class QueryParamsScenarioInline(admin.TabularInline):
    model = model.QueryParamsScenario


class InjectHeaderInline(admin.TabularInline):
    model = model.InjectHeader


@admin.register(model.InjectHeader)
class InjectHeaderAdmin(admin.ModelAdmin):
    list_display = ['session_type', 'key', 'value']
    list_filter = ['session_type']
    search_fields = ['key', 'value']


@admin.register(model.ExposedUrl)
class ExposedUrlAdmin(admin.ModelAdmin):
    list_display = ['session', 'vng_endpoint', 'subdomain', 'id', 'test_session', 'docker_url']
    list_filter = ['session__name']
    search_fields = ['session__name']


@admin.register(model.SessionType)
class SessionTypeAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'name',
        'standard',
        'role',
        'application',
        'version',
        'header',
        'db_data',
        'active'
    ]
    list_filter = ['name']
    list_editable = ('active',)
    search_fields = ['name']

    inlines = [VNGEndpointInline, InjectHeaderInline]
    form = SessionTypeFormAdmin


@admin.register(model.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        'started',
        'stopped',
        'session_type',
        'user',
        'status',
        'name',
        'id',
        'error_message',
        'deploy_status',
        'build_version',
    ]
    list_filter = ['user']
    search_fields = ['name', 'id', 'user__username']
    inlines = [ExposedUrlInline]


@admin.register(model.SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    search_fields = ['session__name', 'date']
    list_display = ['date', 'session', 'response_status']


@admin.register(model.ScenarioCaseCollection)
class ScenarioCaseCollectionAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = [
        'name',
    ]
    inlines = [ScenarioCaseInline]


@admin.register(model.ScenarioCase)
class ScenarioCaseAdmin(OrderedModelAdmin):
    list_display = [
        'url',
        'move_up_down_links',
        'http_method',
        'query_params',
        'collection'
    ]
    inlines = [QueryParamsScenarioInline]
    ordering = ('collection', 'order',)
    list_filter = ['collection']


@admin.register(model.QueryParamsScenario)
class QueryParamsScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario_case', 'expected_value']
    list_filter = ['scenario_case']


@admin.register(model.TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = [
        'test_result',
        'json_result',
    ]


@admin.register(model.VNGEndpoint)
class VNGEndpointAdmin(OrderedModelAdmin):
    list_display = [
        'url',
        'move_up_down_links',
        'name',
        'path',
        'docker_image',
        'session_type',
        'scenario_collection',
        'port',
        'test_file',
    ]
    ordering = ('session_type', 'order',)
    list_filter = ['session_type']


@admin.register(model.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'scenario_case',
        'session_log',
        'result'
    ]


@admin.register(model.EnvironmentalVariables)
class EnvironmentalVariablesAdmin(admin.ModelAdmin):
    list_display = [
        'vng_endpoint',
        'key',
        'value'
    ]
