from rest_framework import routers

from .viewsets import DesignRuleSessionViewSet, DesignRuleTestSuiteViewSet


app_name = "design_rules_api"


router = routers.SimpleRouter(trailing_slash=False)
router.register('designrule-testsuite', DesignRuleTestSuiteViewSet, 'test_suite')
router.register('designrule-session', DesignRuleSessionViewSet, 'session')
# router.register('designrule-result', DesignRuleResultViewSet, 'result')


urlpatterns = router.urls
# api_v1_design_rules:session-detail

