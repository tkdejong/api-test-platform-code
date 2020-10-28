from rest_framework import serializers

from vng.design_rules.models import DesignRuleTestSuite, DesignRuleSession, DesignRuleResult


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


class DesignRuleResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignRuleResult
        fields = ("rule_type", "success", "errors")
        read_only_fields = ("rule_type", "success", "errors")


class DesignRuleSessionSerializer(serializers.ModelSerializer):
    results = DesignRuleResultSerializer(many=True, read_only=True)
    # success = serializers.SerializerMethodField(read_only=True, source="successful")

    class Meta:
        model = DesignRuleSession
        fields = ("uuid", "started_at", "percentage_score", "results")
        read_only_fields = ("uuid", "started_at", "percentage_score")

    # def get_success(self, obj):
    #     return obj.successful()


class DesignRuleTestSuiteSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    sessions = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api_v1_design_rules:session-detail'
    )

    class Meta:
        model = DesignRuleTestSuite
        fields = ("uuid", "api_endpoint", "sessions")
        read_only_fields = ("uuid", )
