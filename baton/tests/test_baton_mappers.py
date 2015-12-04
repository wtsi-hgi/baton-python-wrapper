import unittest
from typing import Iterable

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import File, SearchCriterion
from testwithbaton import TestWithBatonSetup, get_irods_server_from_environment_if_defined
from testwithbaton.helpers import SetupHelper

from baton._baton_mappers import BatonIrodsMapper, BatonBinary, BatonIrodsFileMapper
from baton.models import IrodsMetadata
from baton.tests._helpers import create_irods_file
from baton.tests._stubs import StubBatonIrodsMapper

_FILE_NAMES = ["file_name_1", "file_name_2", "file_name_3"]
_ATTRIBUTES = ["attribute_1", "attribute_2"]
_VALUES = ["value_1", "value_2", "value_3"]
_UNUSED_VALUE = "value_4"


class TestBatonIrodsMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsMapper`.
    """
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
        self.assertRaises(ValueError, StubBatonIrodsMapper, ".", "")

    def test_instantiate_with_valid_baton_directory(self):
        self.test_with_baton.setup()
        StubBatonIrodsMapper(self.test_with_baton.baton_location, "")

    def test_run_baton_query(self):
        self.test_with_baton.setup()
        baton_mapper = StubBatonIrodsMapper(self.test_with_baton.baton_location, "")

        baton_out_as_json = baton_mapper.run_baton_query(BatonBinary.BATON)[0]
        self.assertIn("avus", baton_out_as_json)
        self.assertEquals(baton_out_as_json["avus"], [])

    def tearDown(self):
        self.test_with_baton.tear_down()


class TestBatonIrodsFileMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsFileMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()
        self.test_with_baton.setup()
        self.mapper = BatonIrodsFileMapper(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

        self.metadata_1 = IrodsMetadata({_ATTRIBUTES[0]: {"something_else", _VALUES[0]}})
        self.metadata_2 = IrodsMetadata({_ATTRIBUTES[1]: {_VALUES[1]}})
        self.metadata_1_2 = TestBatonIrodsFileMapper._combine_metadata([self.metadata_1, self.metadata_2])
        self.search_criterion_1 = SearchCriterion(_ATTRIBUTES[0], _VALUES[0], ComparisonOperator.EQUALS)
        self.search_criterion_2 = SearchCriterion(_ATTRIBUTES[1], _VALUES[1], ComparisonOperator.EQUALS)

    def test_get_by_metadata_when_no_metadata(self):
        retrieved_files = self.mapper.get_by_metadata(
            SearchCriterion(_ATTRIBUTES[0], _UNUSED_VALUE, ComparisonOperator.EQUALS))
        self.assertEquals(len(retrieved_files), 0)

    def test_get_by_metadata_when_single_criterion_match_single_file(self):
        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1)

        retrieved_files = self.mapper.get_by_metadata(self.search_criterion_1)
        self.assertEquals(retrieved_files[0], file_1)
        self.assertCountEqual(retrieved_files, [file_1])

    def test_get_by_metadata_when_multiple_criterions_match_single_file(self):
        search_criteria = SearchCriteria([self.search_criterion_1, self.search_criterion_2])

        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1_2)
        create_irods_file(self.test_with_baton, _FILE_NAMES[1], self.metadata_1)

        retrieved_files = self.mapper.get_by_metadata(search_criteria)
        self.assertCountEqual(retrieved_files, [file_1])

    def test_get_by_metadata_when_single_criterion_match_multiple_files(self):
        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1_2)
        file_2 = create_irods_file(self.test_with_baton, _FILE_NAMES[1], self.metadata_1)
        self.setup_helper.create_irods_file(_FILE_NAMES[2])

        retrieved_files = self.mapper.get_by_metadata(self.search_criterion_1)
        self.assertCountEqual(retrieved_files, [file_1, file_2])

    def test_get_by_metadata_when_multiple_criterions_match_multiple_files(self):
        search_criteria = SearchCriteria([self.search_criterion_1, self.search_criterion_2])

        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1_2)
        file_2 = create_irods_file(self.test_with_baton, _FILE_NAMES[1], self.metadata_1_2)
        self.setup_helper.create_irods_file(_FILE_NAMES[2])

        retrieved_files = self.mapper.get_by_metadata(search_criteria)
        self.assertCountEqual(retrieved_files, [file_1, file_2])

    def test_get_by_metadata_when_metadata_not_required_for_file(self):
        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1)

        retrieved_files = self.mapper.get_by_metadata(self.search_criterion_1, load_metadata=False)

        self.assertIsNone(retrieved_files[0].metadata)
        file_1.metadata = None
        self.assertEquals(retrieved_files[0], file_1)

    def test_get_by_path_when_file_does_not_exist(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_by_path, File("/invalid", "name"))

    def test_get_by_path_with_single_file(self):
        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1)

        retrieved_files = self.mapper.get_by_path(file_1)
        self.assertCountEqual(retrieved_files, [file_1])

    def test_get_by_path_with_multiple_files(self):
        files = [
            create_irods_file(self.test_with_baton, _FILE_NAMES[i], self.metadata_1) for i in range(len(_FILE_NAMES))]

        retrieved_files = self.mapper.get_by_path(files)
        self.assertCountEqual(retrieved_files, files)

    def test_get_by_path_with_multiple_files_when_some_do_not_exist(self):
        files = [
            create_irods_file(self.test_with_baton, _FILE_NAMES[i], self.metadata_1) for i in range(len(_FILE_NAMES))]

        self.assertRaises(FileNotFoundError, self.mapper.get_by_path, files + [File("/invalid", "name")])

    def test_get_by_path_when_metadata_not_required(self):
        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1)

        retrieved_files = self.mapper.get_by_path(file_1, load_metadata=False)

        self.assertIsNone(retrieved_files[0].metadata)
        file_1.metadata = None
        self.assertEquals(retrieved_files[0], file_1)

    def get_in_collection_when_file_instead_of_collection(self):
        self.assertRaises(ValueError, self.mapper.get_in_collection, File("/", ""))

    def get_in_collection_when_single_file_instead_of_collection(self):
        collections = [File(""), File(""), File("", "")]
        self.assertRaises(ValueError, self.mapper.get_in_collection, collections)

    def get_in_collection_when_collection_does_not_exist(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_in_collection, File("/invalid"))

    def get_in_collection_with_single_collection(self):
        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1)

        retrieved_files = self.mapper.get_in_collection(file_1.directory)
        self.assertCountEqual(retrieved_files, [file_1])

    def get_in_collection_with_multiple_collections(self):
        files = [
            create_irods_file(self.test_with_baton, _FILE_NAMES[i], self.metadata_1) for i in range(len(_FILE_NAMES))]
        for i in range(len(files) - 1):
            assert files[i].directory == files[i + 1]

        # FIXME: Make multiple collections

        retrieved_files = self.mapper.get_in_collection(files[0].directory)
        self.assertCountEqual(retrieved_files, files)

    def get_in_collection_with_multiple_collections_when_some_do_not_exist(self):
        files = [
            create_irods_file(self.test_with_baton, _FILE_NAMES[i], self.metadata_1) for i in range(len(_FILE_NAMES))]
        for i in range(len(files) - 1):
            assert files[i].directory == files[i + 1]

        self.assertRaises(FileNotFoundError, self.mapper.get_in_collection, files[0].directory + [File("/invalid")])

    def get_in_collection_when_metadata_not_required(self):
        file_1 = create_irods_file(self.test_with_baton, _FILE_NAMES[0], self.metadata_1)

        retrieved_files = self.mapper.get_in_collection(file_1.directory, load_metadata=False)

        self.assertIsNone(retrieved_files[0].metadata)
        file_1.metadata = None
        self.assertEquals(retrieved_files[0], file_1)

    def tearDown(self):
        self.test_with_baton.tear_down()

    @staticmethod
    def _combine_metadata(metadata_collection: Iterable[IrodsMetadata]) -> IrodsMetadata:
        """
        Combines n metadata objects into a single metadata object. Key values are merged, duplicate values are removed.
        :param metadata_collection: the collection of metadata to combine
        :return: the combined metadata
        """
        combined = IrodsMetadata()
        for metadata in metadata_collection:
            for key, value in metadata.items():
                if key not in combined:
                    combined[key] = value
                else:
                    combined[key].add(value)
        return combined


if __name__ == "__main__":
    unittest.main()
