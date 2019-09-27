import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone

from django.db import transaction
from django.db.models import Prefetch

from rest_framework import permissions, viewsets, mixins, views
from rest_framework.response import Response
from rest_framework.decorators import action
# from rest_framework.exceptions import bad_request

from rest_framework.authentication import (
    SessionAuthentication, TokenAuthentication
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import vng.postman.utils as ptm

from vng.apiAuthentication.authentication import CustomTokenAuthentication

from .serializers import ServerRunSerializer, ServerRunPayloadExample, ServerRunResultShield, PostmanTestSerializer
from .models import ServerRun, PostmanTestResult, PostmanTest
from .task import execute_test
from ..utils import choices


def get_server_run_badge(server_run, label):
    res = server_run.get_execution_result()
    is_error = True
    if res is None:
        message = 'No results'
        color = 'inactive'
    elif res:
        message = 'Success'
        color = 'green'
        is_error = False
    else:
        message = 'Failed'
        color = 'red'
    result = {
        'schemaVersion': 1,
        'label': label,
        'message': message,
        'color': color,
        'isError': is_error,
    }
    return result


class ServerRunViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    """
    create:
    Create a provider-run.

    Create a new provider-run instance.


    retrieve:
    Provider-run detail.

    Return the given provider-run.

    list:
    Provider-run list.

    Return a list of all the existing provider-run.
    """
    authentication_classes = (CustomTokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServerRunSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(request_body=ServerRunPayloadExample)
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)

    def get_queryset(self):
        return ServerRun.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('endpoint_set', to_attr='endpoints'),
            Prefetch('endpoint_set__test_scenario_url'))

    @transaction.atomic
    def perform_create(self, serializer):
        if 'endpoints' in serializer._kwargs['data']:
            server = serializer.save(user=self.request.user, pk=None, started=timezone.now(), endpoint_list=serializer._kwargs['data'].pop('endpoints'))
        else:
            server = serializer.save(user=self.request.user, pk=None, started=timezone.now())


class TriggerServerRunView(viewsets.ViewSet):
    authentication_classes = (CustomTokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, )

    def update(self, request, uuid):
        server = get_object_or_404(ServerRun, uuid=uuid)
        if server.status == choices.StatusWithScheduledChoices.stopped:
            raise Http404("Server already stopped")
        execute_test.delay(server.pk, scheduled=True)
        return JsonResponse({"asd": uuid})


class ResultServerViewShield(views.APIView):
    """
    Provider run badge detail

    Return the badge information of a specific provider run
    """

    @swagger_auto_schema(responses={200: ServerRunResultShield})
    def get(self, request, uuid=None):
        server = get_object_or_404(ServerRun, uuid=uuid)
        return JsonResponse(get_server_run_badge(server, 'API Test Platform'))


class ResultServerView(views.APIView):
    """
    Result of a Session

    Return for each scenario case related to the session, if that call has been performed and the global outcome.
    """
    authentication_classes = (CustomTokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        self.server_run = get_object_or_404(ServerRun, uuid=self.kwargs['uuid'])
        return self.server_run

    def get(self, request, uuid, *args, **kwargs):
        server_run = self.get_object()
        if not server_run.is_stopped():
            res = {
                'Information': 'The tests against the provider-run is undergoing.'
            }
            response = HttpResponse(json.dumps(res))
            response['Content-Type'] = 'application/json'
            return response
        postman_res = PostmanTestResult.objects.filter(server_run=server_run)
        response = []
        for postman in postman_res:
            postman.json = postman.get_json_obj()
            postman_res_output = {
                'time': postman.get_json_obj_info()['run']['timings']['started'],
                'calls': []
            }
            for call in postman.json:
                _call = {
                    'name': call['item']['name'],
                    'request': call['request']['method'],
                    'response': call['response']['code'],
                }
                if 'assertions' in call:
                    for _assertion in call['assertions']:
                        _assertion['result'] = 'failed' if 'error' in _assertion else 'success'
                    _call['assertions'] = call['assertions']
                else:
                    _call['assertions'] = []

                if call['response']['code'] in ptm.get_error_codes():
                    _call['status'] = 'Error'
                else:
                    _call['status'] = 'Success'
                postman_res_output['calls'].append(_call)

            postman_res_output['status'] = postman.status
            response.append(postman_res_output)
        return JsonResponse(response, safe=False)


class PostmanTestViewset(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
    Postman test list

    Return a list of all the existing Postman tests

    get_specific_version:
    Retrieve a specific version of a Postman test

    Return the Postman test collection that has the given name and version

    get_all_versions:
    Retrieve all versions of a Postman test

    Return all the possible versions of a Postman test

    retrieve:
    Postman test detail

    Return a specific Postman test
    """
    serializer_class = PostmanTestSerializer
    queryset = PostmanTest.objects.all()

    @action(methods=['GET'], detail=False, url_path='get_versions/(?P<name>[^/.]+)')
    def get_all_versions(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.serializer_class(qs.filter(name=kwargs.get('name')), many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='get_version/(?P<name>[^/.]+)/(?P<version>[0-9]\.[0-9]\.[0-9])')
    def get_specific_version(self, request, *args, **kwargs):
        qs = self.get_queryset()
        obj = get_object_or_404(PostmanTest, name=kwargs.get('name'), version=kwargs.get('version'))
        return Response(obj.valid_file)


class ServerRunLatestResultView(views.APIView):
    """
    Retrieve the latest badge for a test scenario

    Return the badge information of the latest provider run given a combination of
    test scenario name and username of the user that starten the provider run
    """

    @swagger_auto_schema(
        responses={200: ServerRunResultShield},
        manual_parameters=[
            openapi.Parameter(
                'name',
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Name of the test scenario'
            ),
            openapi.Parameter(
                'user',
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Name of the user that started the provider run for the test scenario'
            ),
        ])
    def get(self, request, name, user):
        latest_server_run = ServerRun.objects.filter(
            test_scenario__name=name,
            user__username=user
        ).order_by('-stopped').first()
        if not latest_server_run:
            raise Http404
        return JsonResponse(get_server_run_badge(latest_server_run, 'API Test Platform'))
