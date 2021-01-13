from copy import copy

from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers, validators

from vng.design_rules.choices import DesignRuleChoices
from vng.design_rules.models import DesignRuleTestSuite, DesignRuleSession, DesignRuleResult, DesignRuleTestVersion, DesignRuleTestOption


class TestVersionField(serializers.Field):
    default_error_messages = {
        'required': _('This field is required.'),
        'null': _('This field may not be null.'),
        'invalid': _('A valid integer is required.'),
        'does_not_exist': _('Invalid pk "{pk_value}" - object does not exist.'),
        'version_inactive': _('The test version "{test_version}" is inactive.'),
    }

    def to_internal_value(self, data):
        try:
            data = int(str(data))
            test_versions = DesignRuleTestVersion.objects.filter(pk=data)
            if test_versions.exists():
                test_version = test_versions.first()
                test_versions = test_versions.filter(is_active=True)
                if test_versions.exists():
                    return test_version
                self.fail('version_inactive', test_version=test_version)
                return data
            else:
                self.fail('does_not_exist', pk_value=data)
                return data
            test_version = DesignRuleTestVersion.objects.get(pk=data)
            return test_version
        except (ValueError, TypeError):
            self.fail('invalid')
            return data

    def to_representation(self, value):
        return value


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if "request" in self.context:
            fields = self.context['request'].query_params.get('fields')
            if fields:
                fields = fields.split(',')
                # Drop any fields that are not specified in the `fields` argument.
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)


class NoneSerializer(serializers.Serializer):
    pass


class StartSessionSerializer(serializers.Serializer):
    test_version = TestVersionField()


class DesignRuleTestOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignRuleTestOption
        fields = ("rule_type", )
        read_only_fields = ("rule_type", )


class DesignRuleTestVersionSerializer(serializers.ModelSerializer):
    test_rules = DesignRuleTestOptionSerializer(many=True, read_only=True)

    class Meta:
        model = DesignRuleTestVersion
        fields = ("id", "version", "name", "test_rules")
        read_only_fields = ("id", "version", "name")


class DesignRuleResultSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    rule_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DesignRuleResult
        fields = ("rule_type", "success", "errors", "warnings", "url", "description")
        read_only_fields = ("rule_type", "success", "errors", "warnings")

    def get_rule_type(self, obj):
        return obj.get_rule_type_display()

    def get_url(self, obj):
        choice = DesignRuleChoices.get_choice(obj.rule_type)
        return choice.url

    def get_description(self, obj):
        choice = DesignRuleChoices.get_choice(obj.rule_type)
        return choice.description


class DesignRuleSessionSerializer(serializers.ModelSerializer):
    results = DesignRuleResultSerializer(many=True, read_only=True)
    test_version = serializers.SerializerMethodField()
    # success = serializers.SerializerMethodField(read_only=True, source="successful")

    class Meta:
        model = DesignRuleSession
        fields = ("uuid", "started_at", "percentage_score", "test_version", "results")
        read_only_fields = ("uuid", "started_at", "percentage_score")

    def get_test_version(self, obj):
        return obj.test_version.version


class DesignRuleTestSuiteSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    sessions = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        lookup_field="uuid",
        view_name='api_v1_design_rules:session-detail'
    )
    api_endpoint = serializers.URLField(validators=[URLValidator(message=_('Enter a valid URL.'))])
    specification_url = serializers.URLField(validators=[URLValidator(message=_('Enter a valid URL.'))], required=False)

    class Meta:
        model = DesignRuleTestSuite
        fields = ("uuid", "api_endpoint", "specification_url", "sessions")
        read_only_fields = ("uuid", )

    def create(self, validated_data):
        instance, _ = DesignRuleTestSuite.objects.get_or_create(api_endpoint=validated_data.get("api_endpoint"), defaults={
            "specification_url": validated_data.get("specification_url"),
        })

        return instance
