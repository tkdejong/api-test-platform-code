from django.test import TestCase

from .factories import (
    SessionTypeFactory, ScenarioCaseFactory, VNGEndpointFactory, ScenarioCaseCollectionFactory
)

class ScenarioCaseRetrievalTests(TestCase):

    def test_retrieve_scenario_cases_for_session_type(self):
        # Create multiple collections
        collection1 = ScenarioCaseCollectionFactory(name='1')
        collection2 = ScenarioCaseCollectionFactory(name='2')
        _ = ScenarioCaseCollectionFactory(name='3')

        _ = ScenarioCaseFactory(collection=collection1, url='/test1')
        _ = ScenarioCaseFactory(collection=collection2, url='/test2a')
        _ = ScenarioCaseFactory(collection=collection2, url='/test2b')

        sessiontype1 = SessionTypeFactory(name='type1')
        sessiontype2 = SessionTypeFactory(name='type2')

        # Add collections 1 and 2 to endpoints linked to sessiontype1
        _ = VNGEndpointFactory(
            session_type=sessiontype1,
            scenario_collection=collection1
        )
        _ = VNGEndpointFactory(
            session_type=sessiontype1,
            scenario_collection=collection2
        )

        # Add collection1 to an endpoint for sessiontype2 as well
        _ = VNGEndpointFactory(
            session_type=sessiontype2,
            scenario_collection=collection1
        )

        # Verify that the correct scenario cases are retrieved
        scenario_cases = sessiontype1.scenario_cases
        urls = ['/test1', '/test2a', '/test2b']
        for i, case in enumerate(scenario_cases):
            with self.subTest(case=case):
                self.assertEqual(case.url, urls[i])

        scenario_cases2 = sessiontype2.scenario_cases
        self.assertEqual(scenario_cases2.count(), 1)
        self.assertEqual(scenario_cases2.first().url, '/test1')


