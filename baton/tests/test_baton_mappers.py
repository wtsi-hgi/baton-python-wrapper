import unittest
from typing import List

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import File, SearchCriterion
from testwithbaton import TestWithBatonSetup, get_irods_server_from_environment_if_defined
from testwithbaton.helpers import SetupHelper

from baton._baton_mappers import BatonIrodsMapper, BatonIrodsMetadataMapper, BatonBinary, BatonIrodsFileMapper
from baton.models import IrodsFile, IrodsMetadata

_FILE_NAME_1 = "file_name_1"
_FILE_NAME_2 = "file_name_2"
_FILE_NAME_3 = "file_name_3"
_ATTRIBUTE_1 = "attribute_1"
_VALUE_1 = "value_1"
_ATTRIBUTE_2 = "attribute_2"
_VALUE_2 = "value_2"


class TestBatonIrodsMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsMapper`.
    """
    class _StubBatonIrodsMapper(BatonIrodsMapper):
        pass

    def setUp(self):
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

    def test_run_baton_query(self):
        self.test_with_baton.setup()
        baton_mapper = TestBatonIrodsMapper._StubBatonIrodsMapper(self.test_with_baton.baton_location, "")

        baton_out_as_json = baton_mapper.run_baton_query(BatonBinary.BATON)
        self.assertIn("avus", baton_out_as_json)
        self.assertEquals(baton_out_as_json["avus"], [])

    def tearDown(self):
        self.test_with_baton.tear_down()


class TestBatonIrodsMetadataMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsMetadataMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()
        self.test_with_baton.setup()
        self.metadata_mapper = BatonIrodsMetadataMapper(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

        self.metadata_1 = IrodsMetadata({_ATTRIBUTE_1: ["something_else", _VALUE_1]})
        self.metadata_2 = IrodsMetadata({_ATTRIBUTE_2: _VALUE_2})

    def test_get_for_file_that_does_not_exist(self):
        self.assertRaises(FileNotFoundError, self.metadata_mapper.get_for_file, File("/", "invalid"))

    def test_get_for_file_with_no_metadata(self):
        file = self.setup_helper.create_irods_file(_FILE_NAME_1)

        metadata = self.metadata_mapper.get_for_file(file)
        self.assertEqual(len(metadata), 0)

    def test_get_for_file_with_metadata(self):
        file = self.setup_helper.create_irods_file(_FILE_NAME_1)

        self.setup_helper.add_irods_metadata_to_file(file, self.metadata_1)
        self.setup_helper.add_irods_metadata_to_file(file, self.metadata_2)

        metadata = self.metadata_mapper.get_for_file(file)
        self.assertEquals(len(metadata), 2)
        for key, values in metadata.items():
            self.assertIn(IrodsMetadata({key: values}), [self.metadata_1, self.metadata_2])

    def tearDown(self):
        self.test_with_baton.tear_down()


class TestBatonIrodsFileMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsFileMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()
        self.test_with_baton.setup()
        self.file_mapper = BatonIrodsFileMapper(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

        self.metadata_1 = IrodsMetadata({_ATTRIBUTE_1: ["something_else", _VALUE_1]})
        self.metadata_2 = IrodsMetadata({_ATTRIBUTE_2: _VALUE_2})
        self.search_criterion_1 = SearchCriterion(_ATTRIBUTE_1, _VALUE_1, ComparisonOperator.EQUALS)
        self.search_criterion_2 = SearchCriterion(_ATTRIBUTE_2, _VALUE_2, ComparisonOperator.EQUALS)
        self.file_1 = self.setup_helper.create_irods_file(_FILE_NAME_1)
        self.file_2 = self.setup_helper.create_irods_file(_FILE_NAME_2)

    def test_get_by_metadata_attribute_when_no_metadata(self):
        retrieved_irods_files = self.file_mapper.get_by_metadata_attribute(
            SearchCriterion(_ATTRIBUTE_1, _VALUE_1, ComparisonOperator.EQUALS))
        self.assertEquals(len(retrieved_irods_files), 0)

    def test_get_by_metadata_attribute_when_single_criterion_match_single_file(self):
        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_1)

        retrieved_irods_files = self.file_mapper.get_by_metadata_attribute(self.search_criterion_1)
        self.assertCountEqual(
            TestBatonIrodsFileMapper._cast_irods_files_to_files(retrieved_irods_files), [self.file_1])

    def test_get_by_metadata_attribute_when_multiple_criterions_match_single_file(self):
        search_criteria = SearchCriteria([self.search_criterion_1, self.search_criterion_2])

        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_1)
        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_2)
        self.setup_helper.add_irods_metadata_to_file(self.file_2, self.metadata_1)

        retrieved_irods_files = self.file_mapper.get_by_metadata_attribute(search_criteria)
        self.assertCountEqual(
            TestBatonIrodsFileMapper._cast_irods_files_to_files(retrieved_irods_files), [self.file_1])

    def test_get_by_metadata_attribute_when_single_criterion_match_multiple_files(self):
        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_1)
        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_2)
        self.setup_helper.add_irods_metadata_to_file(self.file_2, self.metadata_1)
        self.setup_helper.create_irods_file(_FILE_NAME_3)

        retrieved_irods_files = self.file_mapper.get_by_metadata_attribute(self.search_criterion_1)
        self.assertCountEqual(
            TestBatonIrodsFileMapper._cast_irods_files_to_files(retrieved_irods_files), [self.file_1, self.file_2])

    def test_get_by_metadata_attribute_when_multiple_criterions_match_multiple_files(self):
        search_criteria = SearchCriteria([self.search_criterion_1, self.search_criterion_2])

        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_1)
        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_2)
        self.setup_helper.add_irods_metadata_to_file(self.file_2, self.metadata_1)
        self.setup_helper.add_irods_metadata_to_file(self.file_2, self.metadata_2)
        self.setup_helper.create_irods_file(_FILE_NAME_3)

        retrieved_irods_files = self.file_mapper.get_by_metadata_attribute(search_criteria)
        self.assertCountEqual(
            TestBatonIrodsFileMapper._cast_irods_files_to_files(retrieved_irods_files), [self.file_1, self.file_2])

    def test_get_by_metadata_attribute_retrieves_checksums(self):
        self.setup_helper.add_irods_metadata_to_file(self.file_1, self.metadata_1)
        ichksum_out = self.setup_helper.run_icommand("ichksum", [self.file_1.file_name])
        checksum = ichksum_out.split('\n')[0].split(' ')[-1]

        retrieved_irods_files = self.file_mapper.get_by_metadata_attribute(self.search_criterion_1)
        self.assertEquals(retrieved_irods_files[0].checksum, checksum)

    def tearDown(self):
        self.test_with_baton.tear_down()

    @staticmethod
    def _cast_irods_files_to_files(irods_files: List[IrodsFile]) -> List[File]:
        return [File(irods_file.directory, irods_file.file_name) for irods_file in irods_files]


if __name__ == '__main__':
    unittest.main()
