from rest_framework import serializers

from .models import TestScenarioUrl, Endpoint, ServerRun, TestScenario, PostmanTest
from .task import execute_test

from django.db import transaction

class TestScenarioUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestScenarioUrl
        fields = ['name']


class EndpointSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = Endpoint
        fields = ['name', 'value']
        extra_kwargs = {
            'value': {
                'source': 'url',
            }
        }

    def get_name(self, obj):
        return obj.test_scenario_url.name

    def create(self, validated_data):
        try:
            name = validated_data.pop('name')
            value = validated_data['value']
            tsu = TestScenarioUrl.objects.get(name=name, test_scenario=validated_data['server'].test_scenario)
            ep = Endpoint.objects.create(test_scenario_url=tsu, url=value, server_run=validated_data['server'])
            return ep
        except Exception:
            raise serializers.ValidationError("The urls names provided do not match")


class ServerRunSerializer(serializers.ModelSerializer):

    endpoints = EndpointSerializer(many=True)

    test_scenario = serializers.SlugRelatedField(
        queryset=TestScenario.objects.filter(active=True),
        slug_field='name',
    )

    class Meta:
        model = ServerRun
        fields = [
            'uuid',
            'test_scenario',
            'started',
            'stopped',
            'client_id',
            'secret',
            'endpoints',
            'status',
            'percentage_exec',
            'status_exec'
        ]
        read_only_fields = ['id', 'started', 'stopped', 'status']

    def create(self, validated_data):
        endpoint_created = []
        if 'endpoint_list' in validated_data:
            endpoints = validated_data.pop('endpoint_list')
            validated_data.pop('endpoints')
            instance = ServerRun.objects.create(**validated_data)
            for ep in endpoints:
                if 'name' in ep and 'value' in ep:
                    ep_serializer = EndpointSerializer()
                    endpoint_created.append(ep_serializer.create({
                        'name': ep['name'],
                        'value': ep['value'],
                        'server': instance
                    }))
        else:
            instance = ServerRun.objects.create(**validated_data)
        instance.endpoints = endpoint_created

        transaction.on_commit(lambda: execute_test.delay(instance.pk))
        return instance


class ServerRunPayloadExample(ServerRunSerializer):

    class Meta(ServerRunSerializer.Meta):
        swagger_schema_fields = {
            'example': {
                "test_scenario": "ZDS 2.0 verification test",
                "client_id": "test-api-s694H3mpvZpd",
                "secret": "JKzXwzfQvQlYpcnvMwIbdLsmymzzpFvC",
                "endpoints": [
                    {
                        "url": "https://ref.tst.vng.cloud/drc/",
                        "test_scenario_url": {
                            "name": "DRC"
                        }
                    },
                    {
                        "url": "https://ref.tst.vng.cloud/ztc/",
                        "test_scenario_url": {
                            "name": "ZTC"
                        }
                    },
                    {
                        "url": "https://ref.tst.vng.cloud/zrc/",
                        "test_scenario_url": {
                            "name": "ZRC"
                        }
                    }
                ]
            },
            'response': {
                'trt': 1
            }
        }


class ServerRunResultShield(serializers.Serializer):
    schemaVersion = serializers.IntegerField(default=1)
    label = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=200)
    color = serializers.CharField(max_length=200)
    isError = serializers.BooleanField()


class PostmanTestSerializer(serializers.ModelSerializer):

    validation_file = serializers.FileField()

    class Meta:
        model = PostmanTest
        fields = ('name', 'version', 'test_scenario', 'validation_file',)
