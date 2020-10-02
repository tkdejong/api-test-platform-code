from rest_framework import serializers

from vng.design_rules.models import DesignRuleTestSuite, DesignRuleSession, DesignRuleResult


class DesignRuleResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignRuleResult
        fields = ("uuid", "design_rule", "rule_type", "success", "errors")
        read_only_fields = ("uuid", "design_rule", "rule_type", "success", "errors")


class DesignRuleSessionSerializer(serializers.ModelSerializer):
    test_suite = serializers.HyperlinkedRelatedField(read_only=True, view_name="api_v1_design_rules:test_suite-detail")
    results = DesignRuleResultSerializer(many=True, read_only=True)

    class Meta:
        model = DesignRuleSession
        fields = ("uuid", "test_suite", "started_at", "json_result", "percentage_score", "results")
        read_only_fields = ("uuid", "test_suite", "started_at", "json_result", "percentage_score")


class DesignRuleTestSuiteSerializer(serializers.ModelSerializer):
    sessions = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api_v1_design_rules:session-detail'
    )

    class Meta:
        model = DesignRuleTestSuite
        fields = ("uuid", "api_endpoint", "sessions")
        read_only_fields = ("uuid", )
