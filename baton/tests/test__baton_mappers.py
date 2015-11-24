import logging
import unittest

from hgicommon.models import Metadata
from testwithbaton import TestWithBatonSetup, get_irods_server_from_environment_if_defined
from testwithbaton.helpers import SetupHelper

from baton._baton_mappers import BatonIrodsMapper, BatonIrodsMetadataMapper


class TestBatonIrodsMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsMapper`.
    """
    class _StubBatonIrodsMapper(BatonIrodsMapper):
        pass

    def setUp(self):
        print(get_irods_server_from_environment_if_defined())
        logging.root.setLevel("DEBUG")
        self.test_with_baton = TestWithBatonSetup(get_irods_server_from_environment_if_defined())

    def test_validate_baton_binaries_location_with_invalid_location(self):
        self.assertFalse(BatonIrodsMapper.validate_baton_binaries_location("invalid"))

    def test_validate_baton_binaries_location_with_non_binaries_location(self):
        self.assertFalse(BatonIrodsMapper.validate_baton_binaries_location("."))

    def test_validate_baton_binaries_location_with_binaries_location(self):
        self.test_with_baton.setup()
        self.assertTrue(BatonIrodsMapper.validate_baton_binaries_location(self.test_with_baton.baton_location))

    def test_instantiate_with_invalid_baton_directory(self):
        self.assertRaises(ValueError, TestBatonIrodsMapper._StubBatonIrodsMapper, ".", "")

    def test_instantiate_with_valid_baton_directory(self):
        self.test_with_baton.setup()
        TestBatonIrodsMapper._StubBatonIrodsMapper(self.test_with_baton.baton_location, "")

    def test__run_command(self):
        baton_mapper = TestBatonIrodsMapper._StubBatonIrodsMapper("", "", skip_baton_binaries_validation=True)
        expected = "hello world"
        out = baton_mapper._run_command(["echo", expected])
        self.assertEquals(out, expected)

    @unittest.skip("Test to run command with input has not yet been implemented")
    def test__run_command_with_input(self):
        raise NotImplementedError()

    def tearDown(self):
        self.test_with_baton.tear_down()


class TestBatonIrodsMetadataMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsMetadataMapper`.
    """
    def setUp(self):
        # self.test_with_baton = TestWithBatonSetup(get_irods_server_from_environment_if_defined())
        self.test_with_baton = TestWithBatonSetup()
        self.test_with_baton.setup()
        self.mapper = BatonIrodsMetadataMapper(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

    def test_get_for_file(self):
        file_name = "test_file"
        file = self.setup_helper.create_irods_file(file_name)

        metadata_1 = Metadata("attribute_1", "value_1")
        self.setup_helper.add_irods_metadata_to_file(file, metadata_1)
        metadata_2 = Metadata("attribute_2", "value_2")
        self.setup_helper.add_irods_metadata_to_file(file, metadata_2)

        print(self.mapper.get_for_file(file))

        self.setup_helper.run_icommand("irm", [file_name])
        self.assertTrue(False)


    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == '__main__':
    unittest.main()
