import unittest
from abc import ABCMeta, abstractmethod

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import File, SearchCriterion
from testwithbaton import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

from baton._baton_mappers import BatonDataObjectMapper, BatonCollectionMapper, _BatonIrodsEntityMapper
from baton.models import IrodsMetadata, IrodsEntity, DataObject, Collection
from baton.tests._helpers import combine_metadata, create_data_object, create_collection

_NAMES = ["name_1", "name_2", "name_3"]
_ATTRIBUTES = ["attribute_1", "attribute_2"]
_VALUES = ["value_1", "value_2", "value_3"]
_UNUSED_VALUE = "value_4"


class _TestBatonIrodsEntityMapper(unittest.TestCase, metaclass=ABCMeta):
    """
    Tests for `_BatonIrodsEntityMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

        self.metadata_1 = IrodsMetadata({_ATTRIBUTES[0]: {"something_else", _VALUES[0]}})
        self.metadata_2 = IrodsMetadata({_ATTRIBUTES[1]: {_VALUES[1]}})
        self.metadata_1_2 = combine_metadata([self.metadata_1, self.metadata_2])
        self.search_criterion_1 = SearchCriterion(_ATTRIBUTES[0], _VALUES[0], ComparisonOperator.EQUALS)
        self.search_criterion_2 = SearchCriterion(_ATTRIBUTES[1], _VALUES[1], ComparisonOperator.EQUALS)

    @abstractmethod
    def create_mapper(self) -> _BatonIrodsEntityMapper:
        """
        Creates a mapper to test with.
        :return: the created mapper
        """
        pass

    @abstractmethod
    def create_irods_entity(self, name: str, metadata: IrodsMetadata()) -> IrodsEntity:
        """
        Creates an iRODS entity to test with
        :param name: the name of the entity to create
        :param metadata: the metadata to give to the entity
        :return: the created entity
        """
        pass

    def test_get_by_metadata_when_no_metadata(self):
        retrieved_entities = self.create_mapper().get_by_metadata(
            SearchCriterion(_ATTRIBUTES[0], _UNUSED_VALUE, ComparisonOperator.EQUALS))
        self.assertEquals(len(retrieved_entities), 0)

    def test_get_by_metadata_when_single_criterion_match_single_file(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1)
        self.assertEquals(retrieved_entities[0], irods_entity_1)
        self.assertCountEqual(retrieved_entities, [irods_entity_1])

    def test_get_by_metadata_when_multiple_criterions_match_single_entity(self):
        search_criteria = SearchCriteria([self.search_criterion_1, self.search_criterion_2])

        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1_2)
        self.create_irods_entity(_NAMES[1], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_metadata(search_criteria)
        self.assertCountEqual(retrieved_entities, [irods_entity_1])

    def test_get_by_metadata_when_single_criterion_match_multiple_entities(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1_2)
        irods_entity_2 = self.create_irods_entity(_NAMES[1], self.metadata_1)
        self.create_irods_entity(_NAMES[2])

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1)
        self.assertCountEqual(retrieved_entities, [irods_entity_1, irods_entity_2])

    def test_get_by_metadata_when_multiple_criterions_match_multiple_entities(self):
        search_criteria = SearchCriteria([self.search_criterion_1, self.search_criterion_2])

        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1_2)
        irods_entity_2 = self.create_irods_entity(_NAMES[1], self.metadata_1_2)
        self.create_irods_entity(_NAMES[2], IrodsMetadata())

        retrieved_entities = self.create_mapper().get_by_metadata(search_criteria)
        self.assertCountEqual(retrieved_entities, [irods_entity_1, irods_entity_2])

    def test_get_by_metadata_when_metadata_not_required_for_entities(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1, load_metadata=False)

        self.assertIsNone(retrieved_entities[0].metadata)
        irods_entity_1.metadata = None
        self.assertEquals(retrieved_entities[0], irods_entity_1)

    def test_get_by_path_when_entity_does_not_exist(self):
        self.assertRaises(FileNotFoundError, self.create_mapper().get_by_path, File("/invalid", "name"))

    def test_get_by_path_with_single_entity(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_path(irods_entity_1)
        self.assertCountEqual(retrieved_entities, [irods_entity_1])

    def test_get_by_path_with_multiple_entities(self):
        irods_entities = [
            self.create_irods_entity(_NAMES[i], self.metadata_1) for i in range(len(_NAMES))]

        retrieved_entities = self.create_mapper().get_by_path(irods_entities)
        self.assertCountEqual(retrieved_entities, irods_entities)

    def test_get_by_path_with_multiple_files_when_some_do_not_exist(self):
        irods_entities = [
            self.create_irods_entity(_NAMES[i], self.metadata_1) for i in range(len(_NAMES))]

        self.assertRaises(
            FileNotFoundError, self.create_mapper().get_by_path, irods_entities + [File("/invalid", "name")])

    def test_get_by_path_when_metadata_not_required(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        print(self.create_mapper())

        retrieved_entities = self.create_mapper().get_by_path(irods_entity_1, load_metadata=False)

        self.assertIsNone(retrieved_entities[0].metadata)
        irods_entity_1.metadata = None
        self.assertEquals(retrieved_entities[0], irods_entity_1)

    def tearDown(self):
        self.test_with_baton.tear_down()


class TestBatonDataObjectMapper(_TestBatonIrodsEntityMapper):
    """
    Tests for `BatonDataObjectMapper`.
    """
    def create_mapper(self) -> BatonDataObjectMapper:
        return BatonDataObjectMapper(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)

    def create_irods_entity(self, file_name: str, metadata: IrodsMetadata()) -> DataObject:
        return create_data_object(self.test_with_baton, file_name, metadata)

    def get_all_in_collection_when_data_object_instead_of_collection(self):
        self.assertRaises(ValueError, self.create_mapper().get_all_in_collection, File("/", ""))

    def get_all_in_collection_when_single_data_object_instead_of_collection(self):
        collections = [File(""), File(""), File("", "")]
        self.assertRaises(ValueError, self.create_mapper().get_all_in_collection, collections)

    def get_all_in_collection_when_collection_does_not_exist(self):
        self.assertRaises(FileNotFoundError, self.create_mapper().get_all_in_collection, File("/invalid"))

    def get_all_in_collection_with_single_collection(self):
        data_object_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_all_in_collection(data_object_1.path)
        self.assertCountEqual(retrieved_entities, [data_object_1])

    # def get_all_in_collection_with_multiple_collections(self):
    #     files = [
    #         self.create_irods_entity(_NAMES[i], self.metadata_1) for i in range(len(_NAMES))]
    #     for i in range(len(files) - 1):
    #         assert files[i].directory == files[i + 1]
    #
    #     self.setup_helper.create_irods_collection("other_collection")
    #     self.
    #
    #
    #     # FIXME: Make multiple collections
    #
    #     retrieved_entities = self.mapper.get_all_in_collection(files[0].directory)
    #     self.assertCountEqual(retrieved_entities, files)

    def get_all_in_collection_with_multiple_collections_when_some_do_not_exist(self):
        data_objects = [self.create_irods_entity(_NAMES[i], self.metadata_1) for i in range(len(_NAMES))]
        for i in range(len(data_objects) - 1):
            assert data_objects[i].path == data_objects[i + 1]

        self.assertRaises(
            FileNotFoundError, self.create_mapper().get_all_in_collection, data_objects[0].path + [File("/invalid")])

    def get_all_in_collection_when_metadata_not_required(self):
        data_object_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_all_in_collection(data_object_1.path, load_metadata=False)

        self.assertIsNone(retrieved_entities[0].metadata)
        data_object_1.metadata = None
        self.assertEquals(retrieved_entities[0], data_object_1)


class TestBatonCollectionMapper(_TestBatonIrodsEntityMapper):
    """
    Tests for `BatonCollectionMapper`.
    """
    def create_mapper(self) -> BatonCollectionMapper:
        return BatonCollectionMapper(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)

    def create_irods_entity(self, name: str, metadata: IrodsMetadata()) -> Collection:
        return create_collection(self.test_with_baton, name, metadata)



test_cases = (TestBatonDataObjectMapper, TestBatonCollectionMapper)
# test_cases = (TestBatonDataObjectMapper, )
del(_TestBatonIrodsEntityMapper)

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite



if __name__ == "__main__":
    unittest.main()
