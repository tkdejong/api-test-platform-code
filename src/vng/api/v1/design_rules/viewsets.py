from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema

from vng.design_rules.models import DesignRuleTestSuite, DesignRuleSession
from vng.servervalidation.serializers import ServerRunResultShield

from .serializers import DesignRuleSessionSerializer, DesignRuleTestSuiteSerializer


class DesignRuleTestSuiteViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = DesignRuleTestSuite.objects.all()
    serializer_class = DesignRuleTestSuiteSerializer

    @action(detail=True, methods=['post'], description="Start a new session for the test suite")
    def start_session(self, request, pk=None):
        obj = self.get_object()
        obj.start_session()


class DesignRuleSessionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = DesignRuleSession.objects.all()
    serializer_class = DesignRuleSessionSerializer

    @swagger_auto_schema(responses={200: ServerRunResultShield})
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

