import unittest

from testwithbaton import TestWithBatonSetup

from baton._baton_mappers import BatonIrodsFileMapper
from baton.api import Connection


class TestConnection(unittest.TestCase):
    """
    Tests for `Connection` class.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()

    def test_correct_mapper_properties(self):
        self.test_with_baton.setup()
        connection = Connection(self.test_with_baton.baton_location, "")

        self.assertIsInstance(connection.file, BatonIrodsFileMapper)

    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == '__main__':
    unittest.main()
