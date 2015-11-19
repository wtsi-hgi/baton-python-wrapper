import unittest
from testwithbaton import TestWithBatonSetup

from baton.irods_mappers import BatonMapper


class TestBatonMapper(unittest.TestCase):
    """
    Tests for `BatonMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()

    def test_validate_baton_binaries_location_with_invalid_location(self):
        self.assertFalse(BatonMapper.validate_baton_binaries_location("invalid"))

    def test_validate_baton_binaries_location_with_non_binaries_location(self):
        self.assertFalse(BatonMapper.validate_baton_binaries_location("."))

    def test_validate_baton_binaries_location_with_binaries_location(self):
        self.test_with_baton.setup()
        self.assertTrue(BatonMapper.validate_baton_binaries_location(self.test_with_baton.baton_location))

    def test__run_command(self):
        baton_mapper = BatonMapper("", "", skip_baton_binaries_validation=True)
        expected = "hello"
        out = baton_mapper._run_command(["echo", expected])
        self.assertEquals(out, expected)

    def test__run_command_with_input(self):
        baton_mapper = BatonMapper("", "", skip_baton_binaries_validation=True)
        expected = "hello"
        out = baton_mapper._run_command(["read", "x"], input_data={"a": expected})

        self.assertEquals(out, expected)



    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == '__main__':
    unittest.main()
