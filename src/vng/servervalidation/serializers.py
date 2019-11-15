from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

from .models import TestScenarioUrl, Endpoint, ServerRun, TestScenario, PostmanTest, Environment
from .task import execute_test

from django.db import transaction

class TestScenarioUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestScenarioUrl
        fields = ['name']


class EndpointSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='test_scenario_url.name', help_text=_(
        "The name of the variable"
    ))

    class Meta:
        model = Endpoint
        fields = ['name', 'value']
        extra_kwargs = {
            'value': {
                'source': 'url',
            }
        }

    def to_internal_value(self, data):
        return data

    def create(self, validated_data):
        try:
            name = validated_data.pop('name')
            value = validated_data['value']
            tsu = TestScenarioUrl.objects.get(name=name, test_scenario=validated_data['environment'].test_scenario)
            ep = Endpoint.objects.create(test_scenario_url=tsu, url=value, environment=validated_data['environment'])
            return ep
        except Exception:
            raise serializers.ValidationError("The urls names provided do not match")


class EnvironmentSerializer(serializers.ModelSerializer):
    endpoints = EndpointSerializer(many=True, source='endpoint_set', required=False)

    class Meta:
        model = Environment
        fields = ('name', 'uuid', 'endpoints')

        extra_kwargs = {
            'endpoints': {
                'help_text': _('The environment that will be used for the provider run')
            }
        }


class ServerRunSerializer(serializers.ModelSerializer):

    environment = EnvironmentSerializer()

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
            'environment',
            'software_version',
            'client_id',
            'secret',
            'status',
            'percentage_exec',
            'status_exec'
        ]
        read_only_fields = ['id', 'started', 'stopped', 'status']

    def create(self, validated_data):
        endpoint_created = []
        env = validated_data.pop('environment')
        created = False
        try:
            environment = Environment.objects.get(
                name=env['name'],
                test_scenario=validated_data['test_scenario'],
                user=self.context['request'].user
            )
        except Environment.DoesNotExist:
            environment = Environment.objects.create(
                name=env['name'],
                test_scenario=validated_data['test_scenario'],
                user=self.context['request'].user
            )
            created = True

        validated_data['environment'] = environment
        if created:
            flattened_endpoints = {ep['name']: ep['value'] for ep in env['endpoint_set'] if 'name' in ep and 'value' in ep}
            testscenariourls = validated_data['test_scenario'].testscenariourl_set.all()

            for test_scenario_url in validated_data['test_scenario'].testscenariourl_set.all():
                value = flattened_endpoints.get(test_scenario_url.name) or test_scenario_url.placeholder
                ep_serializer = EndpointSerializer()
                endpoint_created.append(ep_serializer.create({
                    'name': test_scenario_url.name,
                    'value': value,
                    'environment': environment
                }))

        instance = ServerRun.objects.create(**validated_data)

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
