import requests_mock
import yaml
from django.test import TestCase
from vng.testsession.models import ScenarioCaseCollection, ScenarioCase

class ScenarioCaseGenerateFromOASTests(TestCase):

    def test_generate_scenario_cases_from_oas(self):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', 'https://some.oas.link/oas.json', json={
                'swagger': '2.0',
                'info': {
                    'title': 'test oas',
                },
                'paths': {
                    '/zaken': {
                        'get': {
                            'operationId': 'zaak_list',
                            'summary': 'Alle ZAAKen opvragen',
                            'description': '',
                            'parameters': []
                        },
                        'post': {
                            'operationId': 'zaak_create',
                            'summary': 'Maak een ZAAK aan',
                            'description': '',
                            'parameters': []
                        }
                    },
                }
            })
            collection = ScenarioCaseCollection.objects.create(
                name='test collection',
                oas_link='https://some.oas.link/oas.json'
            )

        scenario_cases = collection.scenariocase_set.all()

        self.assertEqual(scenario_cases.count(), 2)

        self.assertEqual(scenario_cases[0].collection, collection)
        self.assertEqual(scenario_cases[0].url, '/zaken')
        self.assertEqual(scenario_cases[0].http_method, 'GET')

        self.assertEqual(scenario_cases[1].collection, collection)
        self.assertEqual(scenario_cases[1].url, '/zaken')
        self.assertEqual(scenario_cases[1].http_method, 'POST')

    def test_generate_scenario_case_with_path_param(self):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', 'https://some.oas.link/oas.json', json={
                'swagger': '2.0',
                'info': {
                    'title': 'test oas',
                },
                'paths': {
                    '/zaken/{uuid}': {
                        'get': {
                            'operationId': 'zaak_read',
                            'summary': 'Een specifieke ZAAK opvragen',
                            'description': '',
                            'parameters': []
                        },
                        'parameters': [
                            {
                                'name': 'uuid',
                                'in': 'path',
                                'required': True,
                                'type': 'string',
                                'format': 'uuid'
                            }
                        ]
                    }
                }
            })
            collection = ScenarioCaseCollection.objects.create(
                name='test collection',
                oas_link='https://some.oas.link/oas.json'
            )

        scenario_case = collection.scenariocase_set.first()

        self.assertEqual(scenario_case.collection, collection)
        self.assertEqual(scenario_case.url, '/zaken/{uuid}')
        self.assertEqual(scenario_case.http_method, 'GET')

    def test_generate_scenario_case_with_query_params(self):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', 'https://some.oas.link/oas.json', json={
                'swagger': '2.0',
                'info': {
                    'title': 'test oas',
                },
                'paths': {
                    '/zaken': {
                        'get': {
                            'operationId': 'zaak_list',
                            'summary': 'Alle ZAAKen opvragen',
                            'description': '',
                            'parameters': [
                                {
                                    'name': 'identificatie',
                                    'in': 'query',
                                    'description': 'test',
                                    'required': False,
                                    'type': 'string'
                                },
                                {
                                    'name': 'verantwoordelijkeOrganisatie',
                                    'in': 'query',
                                    'description': 'test',
                                    'required': False,
                                    'type': 'string'
                                }
                            ]
                        },
                    },
                }
            })
            collection = ScenarioCaseCollection.objects.create(
                name='test collection',
                oas_link='https://some.oas.link/oas.json'
            )

        scenario_case = collection.scenariocase_set.first()

        self.assertEqual(scenario_case.collection, collection)
        self.assertEqual(scenario_case.url, '/zaken')
        self.assertEqual(scenario_case.http_method, 'GET')

        query_params = scenario_case.queryparamsscenario_set.all()

        self.assertEqual(query_params.count(), 2)

        self.assertEqual(query_params[0].name, 'identificatie')
        self.assertEqual(query_params[1].name, 'verantwoordelijkeOrganisatie')

    def test_generate_scenario_case_with_query_params_local_reference(self):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', 'https://some.oas.link/oas.json', json={
                'swagger': '2.0',
                'info': {
                    'title': 'test oas',
                },
                'paths': {
                    '/zaken': {
                        'get': {
                            'operationId': 'zaak_list',
                            'summary': 'Alle ZAAKen opvragen',
                            'description': '',
                            'parameters': [
                                {
                                    '$ref': '#/components/parameters/identificatie',
                                },
                                {
                                    '$ref': '#/components/parameters/verantwoordelijkeOrganisatie',
                                }
                            ]
                        },
                    },
                },
                'components': {
                    'parameters': {
                        'identificatie': {
                            'name': 'identificatie',
                            'in': 'query',
                            'description': 'test',
                            'required': False,
                            'type': 'string'
                        },
                        'verantwoordelijkeOrganisatie': {
                            'name': 'verantwoordelijkeOrganisatie',
                            'in': 'query',
                            'description': 'test',
                            'required': False,
                            'type': 'string'
                        }
                    }
                }
            })
            collection = ScenarioCaseCollection.objects.create(
                name='test collection',
                oas_link='https://some.oas.link/oas.json'
            )

        scenario_case = collection.scenariocase_set.first()

        self.assertEqual(scenario_case.collection, collection)
        self.assertEqual(scenario_case.url, '/zaken')
        self.assertEqual(scenario_case.http_method, 'GET')

        query_params = scenario_case.queryparamsscenario_set.all()

        self.assertEqual(query_params.count(), 2)

        self.assertEqual(query_params[0].name, 'identificatie')
        self.assertEqual(query_params[1].name, 'verantwoordelijkeOrganisatie')

    def test_generate_scenario_cases_from_oas_yaml(self):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', 'https://some.oas.link/oas.yaml', text='''
                swagger: 2.0
                info:
                    title: test oas yaml
                paths:
                    /zaken:
                        get:
                            operationId: zaak_list
                            summary: Alle ZAAKen opvragen
                            description: ''
                            parameters: []
                        post:
                            operationId: zaak_create
                            summary: Maak een ZAAK aan
                            description: ''
                            parameters: []
            ''')
            collection = ScenarioCaseCollection.objects.create(
                name='test collection',
                oas_link='https://some.oas.link/oas.yaml'
            )

        scenario_cases = collection.scenariocase_set.all()

        self.assertEqual(scenario_cases.count(), 2)

        self.assertEqual(scenario_cases[0].collection, collection)
        self.assertEqual(scenario_cases[0].url, '/zaken')
        self.assertEqual(scenario_cases[0].http_method, 'GET')

        self.assertEqual(scenario_cases[1].collection, collection)
        self.assertEqual(scenario_cases[1].url, '/zaken')
        self.assertEqual(scenario_cases[1].http_method, 'POST')

    def test_no_generate_scenario_cases_without_oas_link(self):
        with requests_mock.Mocker() as m:
            m.register_uri('GET', 'https://some.oas.link/oas.json', json={
                'swagger': '2.0',
                'info': {
                    'title': 'test oas',
                },
                'paths': {
                    '/zaken': {
                        'get': {
                            'operationId': 'zaak_list',
                            'summary': 'Alle ZAAKen opvragen',
                            'description': '',
                            'parameters': []
                        },
                    },
                }
            })
            collection = ScenarioCaseCollection.objects.create(
                name='test collection'
            )

        scenario_cases = collection.scenariocase_set.all()

        self.assertFalse(scenario_cases.exists())

    def test_no_generate_scenario_cases_if_cases_exist_for_collection(self):
        collection = ScenarioCaseCollection.objects.create()
        scenario_case = ScenarioCase.objects.create(
            collection=collection,
            http_method='GET',
            url='/test',
            description='test',
        )
        with requests_mock.Mocker() as m:
            m.register_uri('GET', 'https://some.oas.link/oas.json', json={
                'swagger': '2.0',
                'info': {
                    'title': 'test oas',
                },
                'paths': {
                    '/zaken': {
                        'get': {
                            'operationId': 'zaak_list',
                            'summary': 'Alle ZAAKen opvragen',
                            'description': '',
                            'parameters': []
                        },
                    },
                }
            })
            collection.oas_link = 'https://some.oas.link/oas.json'
            collection.save()

        scenario_cases = collection.scenariocase_set.all()

        self.assertEqual(scenario_cases.count(), 1)

        self.assertEqual(scenario_cases[0].collection, collection)
        self.assertEqual(scenario_cases[0].url, '/test')
        self.assertEqual(scenario_cases[0].http_method, 'GET')
        self.assertEqual(scenario_cases[0].description, 'test')
