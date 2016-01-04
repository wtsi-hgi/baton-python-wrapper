import unittest

from testwithbaton import TestWithBatonSetup

from baton._baton_mappers import BatonDataObjectMapper, BatonCollectionMapper, BatonSpecificQueryMapper
from baton.api import Connection
from baton.tests._settings import BATON_DOCKER_BUILD


class TestConnection(unittest.TestCase):
    """
    Tests for `Connection` class.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)
        self.test_with_baton.setup()

    def test_correct_mapper_properties(self):
        connection = Connection(self.test_with_baton.baton_location, "")

        self.assertIsInstance(connection.data_object, BatonDataObjectMapper)
        self.assertIsInstance(connection.collection, BatonCollectionMapper)
        self.assertIsInstance(connection.specific_query, BatonSpecificQueryMapper)

    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == "__main__":
    unittest.main()
