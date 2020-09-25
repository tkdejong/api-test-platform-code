from celery.utils.log import get_task_logger

from vng.celery.celery import app

from ..models import DesignRuleResult, DesignRuleSession

logger = get_task_logger(__name__)


@app.task
def run_tests(session_id):
    session = DesignRuleSession.objects.get(pk=session_id)
