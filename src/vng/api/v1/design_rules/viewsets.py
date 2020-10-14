from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema

from vng.design_rules.models import DesignRuleTestSuite, DesignRuleSession
from vng.servervalidation.serializers import ServerRunResultShield

from .serializers import DesignRuleSessionSerializer, DesignRuleTestSuiteSerializer, NoneSerializer


START_SESSION_DESCRIPTION = "Start a new session for an existing Design rule Test suite. This will generate new results, without having to add the endpoint(s) again."


class DesignRuleTestSuiteViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Get all the Design rule Test suites that are registered.
    create:
    Create a new Design rule Test suite.
    - This will start a Design rule session. The session is returned in the session list.
    read:
    Get a single Design rule Test suite.
    """
    queryset = DesignRuleTestSuite.objects.all()
    serializer_class = DesignRuleTestSuiteSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(operation_description=START_SESSION_DESCRIPTION, request_body=NoneSerializer, responses={201: DesignRuleSessionSerializer})
    @action(detail=True, methods=['post'], description="Start a new session for the test suite")
    def start_session(self, request, pk=None):
        obj = self.get_object()
        obj.start_session()


class DesignRuleSessionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Get all the Design rule sessions that are registered.
    read:
    Get a single Design rule session.
    """
    queryset = DesignRuleSession.objects.all()
    serializer_class = DesignRuleSessionSerializer
    lookup_field = 'uuid'

    @swagger_auto_schema(operation_description="Get the shields.io badge for a session.", responses={200: ServerRunResultShield})
    @action(detail=True, methods=['get'], description="get the shield bagde")
    def shield(self, request, pk=None):
        session = get_object_or_404(DesignRuleSession, pk=pk)

        if session.percentage_score == 100:
            color = 'green'
            is_error = False
        else:
            color = 'red'
            is_error = True

        result = {
            'schemaVersion': 1,
            'label': 'ATP Design rules',
            'message': session.percentage_score,
            'color': color,
            'isError': is_error,
        }

        return JsonResponse(result)
