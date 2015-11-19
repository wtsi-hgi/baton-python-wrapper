import unittest

from testwithbaton import TestWithBatonSetup

from baton import BatonFileMapper
from baton import BatonMetadataMapper
from baton.api import Connection
from baton.irods_mappers import BatonMapper


class TestConnection(unittest.TestCase):
    """
    Tests for `Connection` class.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()

    def test_correct_mapper_properties(self):
        self.test_with_baton.setup()
        connection = Connection(self.test_with_baton.baton_location, "")

        self.assertIsInstance(connection.metadata, BatonMetadataMapper)
        self.assertIsInstance(connection.file, BatonFileMapper)

    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == '__main__':
    unittest.main()
