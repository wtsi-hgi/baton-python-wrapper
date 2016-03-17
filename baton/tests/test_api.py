import unittest

from baton.api import Connection
from baton._baton_mappers import BatonCollectionMapper, BatonDataObjectMapper, BatonSpecificQueryMapper
from baton.tests._settings import BATON_DOCKER_BUILD
from testwithbaton.api import TestWithBatonSetup


class TestConnection(unittest.TestCase):
    """
    Tests for `Connection` class.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)

    def test_correct_mapper_properties(self):
        self.test_with_baton.setup()
        connection = Connection(self.test_with_baton.baton_location)

        self.assertIsInstance(connection.data_object, BatonDataObjectMapper)
        self.assertIsInstance(connection.collection, BatonCollectionMapper)
        self.assertIsInstance(connection.specific_query, BatonSpecificQueryMapper)

    def test_skip_baton_binaries_validation(self):
        self.assertRaises(ValueError, Connection, "invalid", False)

    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == "__main__":
    unittest.main()
