import unittest
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Sequence
from unittest.mock import MagicMock

from baton._baton_mappers import BatonDataObjectMapper, BatonCollectionMapper, _BatonIrodsEntityMapper, \
    BatonSpecificQueryMapper
from baton.collections import IrodsMetadata
from baton.models import IrodsEntity, DataObject, Collection, PreparedSpecificQuery, SpecificQuery, SearchCriterion
from baton.tests._helpers import combine_metadata, create_data_object, create_collection, synchronise_timestamps
from baton.tests._settings import BATON_DOCKER_BUILD
from baton.tests._stubs import StubBatonCustomObjectMapper
from hgicommon.enums import ComparisonOperator
from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

_NAMES = ["name_1", "name_2", "name_3"]
_ATTRIBUTES = ["attribute_1", "attribute_2"]
_VALUES = ["value_1", "value_2", "value_3"]
_UNUSED_VALUE = "value_4"


class _TestBatonIrodsEntityMapper(unittest.TestCase, metaclass=ABCMeta):
    """
    Tests for `_BatonIrodsEntityMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)
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

    @abstractmethod
    def create_irods_entity(self, name: str, metadata: IrodsMetadata()) -> IrodsEntity:
        """
        Creates an iRODS entity to test with
        :param name: the name of the entity to create
        :param metadata: the metadata to give to the entity
        :return: the created entity
        """

    def test_get_by_metadata_when_no_metadata(self):
        retrieved_entities = self.create_mapper().get_by_metadata(
            SearchCriterion(_ATTRIBUTES[0], _UNUSED_VALUE, ComparisonOperator.EQUALS))
        self.assertEqual(len(retrieved_entities), 0)

    def test_get_by_metadata_when_single_criterion_match_single_file(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1)
        self.assertEqual(retrieved_entities, [irods_entity_1])

    def test_get_by_metadata_when_multiple_criterions_match_single_entity(self):
        search_criteria = [self.search_criterion_1, self.search_criterion_2]

        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1_2)
        self.create_irods_entity(_NAMES[1], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_metadata(search_criteria)
        self.maxDiff = None
        self.assertEqual(retrieved_entities, [irods_entity_1])

    def test_get_by_metadata_when_single_criterion_match_multiple_entities(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1_2)
        irods_entity_2 = self.create_irods_entity(_NAMES[1], self.metadata_1)
        self.create_irods_entity(_NAMES[2], IrodsMetadata())

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1)
        self.maxDiff = None
        self.assertEqual(retrieved_entities, [irods_entity_1, irods_entity_2])

    def test_get_by_metadata_when_multiple_criterions_match_multiple_entities(self):
        search_criteria = [self.search_criterion_1, self.search_criterion_2]

        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1_2)
        irods_entity_2 = self.create_irods_entity(_NAMES[1], self.metadata_1_2)
        self.create_irods_entity(_NAMES[2], IrodsMetadata())

        retrieved_entities = self.create_mapper().get_by_metadata(search_criteria)
        self.maxDiff = None
        self.assertEqual(retrieved_entities, [irods_entity_1, irods_entity_2])

    def test_get_by_metadata_when_metadata_not_required_for_entities(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1, load_metadata=False)

        self.assertIsNone(retrieved_entities[0].metadata)
        irods_entity_1.metadata = None
        self.assertEqual(retrieved_entities[0], irods_entity_1)

    @unittest.skip("Unable to setup a new zone in iRODS")
    def test_get_by_metadata_when_zone_restricted(self):
        new_zone = "newZone"
        self.setup_helper.run_icommand(["iadmin", "mkzone %s remote" % new_zone])

        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)
        irods_entity_2 = self.create_irods_entity(_NAMES[1], self.metadata_1)

        self.setup_helper.run_icommand(["icp", "-r", "%s /%s" % (irods_entity_2.path, new_zone)])
        irods_entity_3 = deepcopy(irods_entity_2)
        irods_entity_3.path = "/%s/%s" % (new_zone, irods_entity_2.path.split("/")[-1])

        mapper = self.create_mapper()
        # Check gets both without specifying zone
        self.assertEqual(mapper.get_by_metadata(self.search_criterion_1), [irods_entity_1, irods_entity_2])
        # Check can zone restrict
        self.assertEqual(mapper.get_by_metadata(self.search_criterion_1, zone=new_zone), [irods_entity_3])

    def test_get_by_path_when_no_paths_given(self):
        retrieved_entities = self.create_mapper().get_by_path([])
        self.assertEqual(len(retrieved_entities), 0)

    def test_get_by_path_when_entity_does_not_exist(self):
        self.assertRaises(FileNotFoundError, self.create_mapper().get_by_path, "/invalid/name")

    def test_get_by_path_with_single_entity(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_path(irods_entity_1.path)
        self.assertEqual(retrieved_entities, [irods_entity_1])

    def test_get_by_path_with_multiple_entities(self):
        irods_entities = [
            self.create_irods_entity(_NAMES[i], self.metadata_1) for i in range(len(_NAMES))]
        paths = [irods_entity.path for irods_entity in irods_entities]

        retrieved_entities = self.create_mapper().get_by_path(paths)
        self.assertEqual(retrieved_entities, irods_entities)

    def test_get_by_path_with_multiple_files_when_some_do_not_exist(self):
        irods_entities = [
            self.create_irods_entity(_NAMES[i], self.metadata_1) for i in range(len(_NAMES))]
        paths = [irods_entity.path for irods_entity in irods_entities]

        self.assertRaises(
            FileNotFoundError, self.create_mapper().get_by_path, paths + ["/invalid/name"])

    def test_get_by_path_when_metadata_not_required(self):
        irods_entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_by_path(irods_entity_1.path, load_metadata=False)

        self.assertIsNone(retrieved_entities[0].metadata)
        irods_entity_1.metadata = None
        self.assertEqual(retrieved_entities, [irods_entity_1])

    def test_get_by_metadata_when_collection_with_matching_metadata(self):
        data_object = self.create_irods_entity(_NAMES[0], self.metadata_1)
        create_collection(self.test_with_baton, _NAMES[1], self.metadata_1_2)

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1)
        self.assertEqual(retrieved_entities, [data_object])

    def test_get_all_in_collection_when_collection_does_not_exist(self):
        self.assertRaises(FileNotFoundError, self.create_mapper().get_all_in_collection, "/invalid")

    def test_get_all_in_collection_when_one_of_multiple_collections_does_not_exist(self):
        collection_paths = [self.setup_helper.create_collection("collection"), "/invalid"]
        self.assertRaises(FileNotFoundError, self.create_mapper().get_all_in_collection, collection_paths)

    def test_get_all_in_collection_when_no_paths_given(self):
        retrieved = self.create_mapper().get_all_in_collection([])
        self.assertEqual(len(retrieved), 0)

    def test_get_all_in_collection_with_single_collection_containing_one_entity(self):
        entity = self.create_irods_entity(_NAMES[0], self.metadata_1)

        retrieved_entities = self.create_mapper().get_all_in_collection(entity.get_collection_path())
        self.assertEqual(retrieved_entities, [entity])

    def test_get_all_in_collection_with_single_collection_containing_multiple_entities(self):
        entity_1 = self.create_irods_entity(_NAMES[0], self.metadata_1)
        entity_2 = self.create_irods_entity(_NAMES[1], self.metadata_2)
        assert entity_1.get_collection_path() == entity_2.get_collection_path()

        retrieved_entities = self.create_mapper().get_all_in_collection(entity_1.get_collection_path())
        self.assertEqual(retrieved_entities, [entity_1, entity_2])

    def test_get_all_in_collection_with_multiple_collections(self):
        collections = []
        entities = []

        for i in range(3):
            collection = self.setup_helper.create_collection("collection_%d" % i)

            for j in range(len(_NAMES)):
                entity = self.create_irods_entity(_NAMES[j], self.metadata_1)
                moved_path = "%s/%s" % (collection, entity.get_name())
                self.setup_helper.run_icommand(["imv", entity.path, moved_path])
                entity.path = moved_path
                synchronise_timestamps(self.test_with_baton, entity)
                entities.append(entity)

            collections.append(collection)

        retrieved_entities = self.create_mapper().get_all_in_collection(collections)
        self.assertEqual(retrieved_entities, entities)

    def test_get_all_in_collection_when_metadata_not_required(self):
        entity = self.create_irods_entity(_NAMES[0], self.metadata_1)
        self.create_irods_entity(_NAMES[1], self.metadata_1)

        retrieved_entities = self.create_mapper().get_all_in_collection(
            entity.get_collection_path(), load_metadata=False)

        self.assertIsNone(retrieved_entities[0].metadata)
        entity.metadata = None
        self.assertEqual(retrieved_entities[0], entity)

    def test_get_all_in_collection_when_collection_contains_data_objects_and_collections(self):
        data_object = self.create_irods_entity(_NAMES[0], self.metadata_1)
        collection = create_collection(self.test_with_baton, _NAMES[1], self.metadata_2)

        retrieved_entities = self.create_mapper().get_all_in_collection(data_object.get_collection_path())

        self.assertEqual(retrieved_entities, [data_object])

    def tearDown(self):
        self.test_with_baton.tear_down()


class TestBatonDataObjectMapper(_TestBatonIrodsEntityMapper):
    """
    Tests for `BatonDataObjectMapper`.
    """
    def create_mapper(self) -> BatonDataObjectMapper:
        return BatonDataObjectMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, metadata: IrodsMetadata()) -> DataObject:
        return create_data_object(self.test_with_baton, name, metadata)


class TestBatonCollectionMapper(_TestBatonIrodsEntityMapper):
    """
    Tests for `BatonCollectionMapper`.
    """
    def create_mapper(self) -> BatonCollectionMapper:
        return BatonCollectionMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, metadata: IrodsMetadata()) -> Collection:
        return create_collection(self.test_with_baton, name, metadata)

    # TODO: Check if this should be in superclass?
    def test_get_by_metadata_when_data_object_with_matching_metadata(self):
        collection = self.create_irods_entity(_NAMES[0], self.metadata_1)
        create_data_object(self.test_with_baton, _NAMES[1], self.metadata_1_2)

        retrieved_entities = self.create_mapper().get_by_metadata(self.search_criterion_1)
        self.assertEqual(retrieved_entities, [collection])


class TestBatonCustomObjectMapper(unittest.TestCase):
    """
    Tests for `BatonCustomObjectMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)
        self.test_with_baton.setup()

        self.mapper = StubBatonCustomObjectMapper(self.test_with_baton.baton_location)
        self.mapper._object_deserialiser = MagicMock(wraps=self.mapper._object_deserialiser)

    def test_get_using_specific_query(self):
        results = self.mapper._get_with_prepared_specific_query(PreparedSpecificQuery("ls"))
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), self.mapper._object_deserialiser.call_count)


class TestBatonInstalledSpecificQueryMapper(unittest.TestCase):
    """
    Tests for `BatonSpecificQueryMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

        self.mapper = BatonSpecificQueryMapper(self.test_with_baton.baton_location)

    def test_get_all(self):
        iquest_ls_response = self.setup_helper.run_icommand(["iquest", "--sql", "ls"])
        expected = TestBatonInstalledSpecificQueryMapper._parse_iquest_ls(iquest_ls_response)
        specific_queries = self.mapper.get_all()
        self.assertCountEqual(specific_queries, expected)

    @staticmethod
    def _parse_iquest_ls(iquest_ls_response: str) -> Sequence[SpecificQuery]:
        """
        Gets the installed specific queries by parsing the output returned by "iquest --sql ls".
        :param iquest_ls_response: the response returned by the iquest command
        :return: the specific queries installed on the iRODS server
        """
        iquest_ls_response_lines = iquest_ls_response.split('\n')
        assert (len(iquest_ls_response_lines) + 1) % 3 == 0

        specific_queries = []
        for i in range(int((len(iquest_ls_response_lines) + 1) / 3)):
            i3 = int(3 * i)
            alias = iquest_ls_response_lines[i3]
            sql = iquest_ls_response_lines[i3 + 1]
            specific_queries.append(SpecificQuery(alias, sql))

        return specific_queries


# Trick required to stop Python's unittest from running the abstract base class as a test
del _TestBatonIrodsEntityMapper


if __name__ == "__main__":
    unittest.main()
