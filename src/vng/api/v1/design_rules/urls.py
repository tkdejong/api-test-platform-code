from django.urls import path

from rest_framework import routers

from .viewsets import DesignRuleSessionViewSet, DesignRuleTestSuiteViewSet, DesignRuleSessionShieldView, DesignRuleTestVersionViewSet


app_name = "design_rules_api"


router = routers.SimpleRouter(trailing_slash=False)
router.register('designrule-testversion', DesignRuleTestVersionViewSet, 'test_versions')
router.register('designrule-testsuite', DesignRuleTestSuiteViewSet, 'test_suite')
router.register('designrule-session', DesignRuleSessionViewSet, 'session')
# router.register('designrule-result', DesignRuleResultViewSet, 'result')


urlpatterns = router.urls + [
    path('designrule-session/shield/<uuid:uuid>', DesignRuleSessionShieldView.as_view(), name='design_rule-shield'),
]
# api_v1_design_rules:session-detail

