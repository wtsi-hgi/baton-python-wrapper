import unittest

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton.tests._baton._settings import BATON_DOCKER_BUILD
from baton.tests._baton._stubs import StubBatonRunner
from testwithbaton.api import TestWithBatonSetup

_NAMES = ["name_1", "name_2", "name_3"]
_ATTRIBUTES = ["attribute_1", "attribute_2"]
_VALUES = ["value_1", "value_2", "value_3"]
_UNUSED_VALUE = "value_4"


class TestBatonRunner(unittest.TestCase):
    """
    Tests for `_BatonRunner`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)

    def test_validate_baton_binaries_location_with_invalid_location(self):
        self.assertFalse(BatonRunner.validate_baton_binaries_location("invalid"))

    def test_validate_baton_binaries_location_with_non_binaries_location(self):
        self.assertFalse(BatonRunner.validate_baton_binaries_location("."))

    def test_validate_baton_binaries_location_with_binaries_location(self):
        self.test_with_baton.setup()
        self.assertTrue(BatonRunner.validate_baton_binaries_location(self.test_with_baton.baton_location))

    def test_instantiate_with_invalid_baton_directory(self):
        self.assertRaises(ValueError, StubBatonRunner, ".", "")

    def test_instantiate_with_valid_baton_directory(self):
        self.test_with_baton.setup()
        StubBatonRunner(self.test_with_baton.baton_location)

    def test_run_baton_query(self):
        self.test_with_baton.setup()
        baton_mapper = StubBatonRunner(self.test_with_baton.baton_location)

        baton_out_as_json = baton_mapper.run_baton_query(BatonBinary.BATON)[0]
        self.assertIn("avus", baton_out_as_json)
        self.assertEquals(baton_out_as_json["avus"], [])

    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == "__main__":
    unittest.main()
