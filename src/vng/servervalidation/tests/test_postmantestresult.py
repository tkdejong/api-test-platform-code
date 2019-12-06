from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .factories import PostmanTestResultFactory


class PostmanTestResultTests(TestCase):

    def test_get_aggregated_results_no_assertions_failed_no_errors(self):
        ptr = PostmanTestResultFactory.create(log_json=SimpleUploadedFile('test.json', b'''
            {
                "run": {
                    "executions": [{"request": {"url": "test"}, "response": {"code": 400}, "item": {"error_test": false}}],
                    "timings": {"started": "100", "stopped": "200"}
                }
            }
        '''))
        res = ptr.get_aggregate_results()

        self.assertDictEqual(res, {
            'assertions': {'passed': 0, 'failed': 0, 'total': 0},
            'calls': {'success': 1, 'failed': 0, 'total': 1}
        })

    def test_get_aggregated_results_no_assertions_failed_with_errors(self):
        ptr = PostmanTestResultFactory.create(log_json=SimpleUploadedFile('test.json', b'''
            {
                "run": {
                    "executions": [{"request": {"url": "test"}, "response": {"code": 400}, "item": {"error_test": true}}],
                    "timings": {"started": "100", "stopped": "200"}
                }
            }
        '''))
        res = ptr.get_aggregate_results()

        self.assertDictEqual(res, {
            'assertions': {'passed': 0, 'failed': 0, 'total': 0},
            'calls': {'success': 0, 'failed': 1, 'total': 1}
        })

    def test_get_aggregated_results_failed_assertion_no_errors(self):
        ptr = PostmanTestResultFactory.create(log_json=SimpleUploadedFile('test.json', b'''
            {
                "run": {
                    "executions": [{
                        "request": {"url": "test"}, "response": {"code": 400}, "item": {"error_test": false},
                        "assertions": [{"error": "bla"}, {}]
                    }],
                    "timings": {"started": "100", "stopped": "200"}
                }
            }
        '''))
        res = ptr.get_aggregate_results()

        self.assertDictEqual(res, {
            'assertions': {'passed': 1, 'failed': 1, 'total': 2},
            'calls': {'success': 0, 'failed': 1, 'total': 1}
        })

    def test_get_aggregated_results_failed_assertion_and_errors(self):
        ptr = PostmanTestResultFactory.create(log_json=SimpleUploadedFile('test.json', b'''
            {
                "run": {
                    "executions": [{
                        "request": {"url": "test"}, "response": {"code": 400}, "item": {"error_test": true},
                        "assertions": [{"error": "bla"}, {}]
                    }],
                    "timings": {"started": "100", "stopped": "200"}
                }
            }
        '''))
        res = ptr.get_aggregate_results()

        self.assertDictEqual(res, {
            'assertions': {'passed': 1, 'failed': 1, 'total': 2},
            'calls': {'success': 0, 'failed': 1, 'total': 1}
        })
