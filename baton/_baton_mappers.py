from abc import ABCMeta, abstractmethod
from typing import Union, Sequence, List, Iterable

import collections

from baton._constants import BATON_SPECIFIC_QUERY_PROPERTY, IRODS_SPECIFIC_QUERY_LS, BATON_AVU_PROPERTY, \
    BATON_COLLECTION_CONTENTS

from baton._baton_runner import BatonBinary, BatonRunner
from baton.json import DataObjectJSONDecoder, CollectionJSONDecoder, DataObjectJSONEncoder, CollectionJSONEncoder, \
    PreparedSpecificQueryJSONEncoder, SpecificQueryJSONDecoder, SearchCriterionJSONEncoder
from baton.mappers import DataObjectMapper, CollectionMapper, IrodsEntityMapper, EntityType, CustomObjectType, \
    CustomObjectMapper, SpecificQueryMapper
from baton.models import DataObject, Collection, PreparedSpecificQuery, SpecificQuery, SearchCriterion


class _BatonIrodsEntityMapper(BatonRunner, IrodsEntityMapper, metaclass=ABCMeta):
    """
    Mapper for iRODS entities, implemented using baton.
    """
    def __init__(self, additional_metadata_query_arguments: List[str], *args, **kwargs):
        """
        Constructor.
        :param additional_metadata_query_arguments: additional arguments to use in baton metadata query
        """
        super().__init__(*args, **kwargs)
        self._additional_metadata_query_arguments = additional_metadata_query_arguments

    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, Iterable[SearchCriterion]],
                       load_metadata: bool=True, zone: str=None) -> Sequence[EntityType]:
        if not isinstance(metadata_search_criteria, collections.Iterable):
            metadata_search_criteria = [metadata_search_criteria]

        used_attributes = dict()
        for search_criteria in metadata_search_criteria:    # type: SearchCriterion
            attribute = search_criteria.attribute
            if search_criteria.attribute in used_attributes:
                raise ValueError("baton does not allow multiple constraints on the same attribute: \"%s\"" % attribute)
            else:
                used_attributes[attribute] = True

        baton_json = {
            BATON_AVU_PROPERTY: SearchCriterionJSONEncoder().default(metadata_search_criteria)
        }
        arguments = self._create_entity_query_arguments(load_metadata)

        if zone is not None:
            arguments.append("--zone %s" % zone)
        # Fixes #6.
        arguments.extend(self._additional_metadata_query_arguments)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_METAQUERY, arguments, input_data=baton_json)
        return self._baton_json_to_irods_entities(baton_out_as_json)

    def get_by_path(self, paths: Union[str, Iterable[str]], load_metadata: bool=True) -> Sequence[EntityType]:
        if not isinstance(paths, list):
            paths = [paths]
        if len(paths) == 0:
            return []

        baton_json = []
        for path in paths:
            path_json = self._path_to_baton_json(path)
            baton_json.append(path_json)
        arguments = self._create_entity_query_arguments(load_metadata)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)
        return self._baton_json_to_irods_entities(baton_out_as_json)

    def _create_entity_query_arguments(self, load_metadata: bool=True) -> List[str]:
        """
        Create arguments to use with baton.
        :param load_metadata: whether baton should load metadata
        :return: the arguments to use with baton
        """
        arguments = ["--acl", "--replicate", "--timestamp"]
        if load_metadata:
            arguments.append("--avu")
        return arguments

    def _baton_json_to_irods_entities(self, entities_as_baton_json: List[dict]) -> List[EntityType]:
        """
        Converts the baton representation of multiple iRODS entities to a list of `EntityType` models.
        :param entities_as_baton_json: the baton serialization representation of the entities
        :return: the equivalent models
        """
        assert(isinstance(entities_as_baton_json, list))

        entities = []
        for file_as_baton_json in entities_as_baton_json:
            entity = self._baton_json_to_irod_entity(file_as_baton_json)
            entities.append(entity)

        return entities

    @abstractmethod
    def _path_to_baton_json(self, path: str) -> dict:
        """
        Converts a path to the type of iRODS entity the mapper deals with, to its JSON representation.
        :param path: the path to convert
        :return: the JSON representation of the path
        """

    @abstractmethod
    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> EntityType:
        """
        Converts the baton representation of an iRODS entity to a list of `EntityType` models.
        :param entity_as_baton_json: the baton serialization representation of the entity
        :return: the equivalent models
        """


class BatonDataObjectMapper(_BatonIrodsEntityMapper, DataObjectMapper):
    """
    iRODS data object mapper, implemented using baton.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(["--obj"], *args, **kwargs)

    def get_all_in_collection(self, collection_paths: Union[str, Iterable[str]], load_metadata: bool=True) \
            -> Sequence[DataObject]:
        if not isinstance(collection_paths, list):
            collection_paths = [collection_paths]
        if len(collection_paths) == 0:
            return []

        baton_json = []
        for path in collection_paths:
            collection = Collection(path)
            collection_json = CollectionJSONEncoder().default(collection)
            baton_json.append(collection_json)
        arguments = self._create_entity_query_arguments(load_metadata)
        arguments.append("--contents")

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)

        data_objects_as_baton_json = []
        for baton_item_as_json in baton_out_as_json:
            data_objects_as_baton_json += baton_item_as_json[BATON_COLLECTION_CONTENTS]

        return self._baton_json_to_irods_entities(data_objects_as_baton_json)

    def _path_to_baton_json(self, path: str) -> dict:
        data_object = DataObject(path)
        return DataObjectJSONEncoder().default(data_object)

    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> DataObject:
        return DataObjectJSONDecoder().decode_dict(entity_as_baton_json)


class BatonCollectionMapper(_BatonIrodsEntityMapper, CollectionMapper):
    """
    iRODS collection mapper, implemented using baton.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(["--coll"], *args, **kwargs)

    def _path_to_baton_json(self, path: str) -> dict:
        collection = Collection(path)
        return CollectionJSONEncoder().default(collection)

    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> Collection:
        return CollectionJSONDecoder().decode_dict(entity_as_baton_json)


class BatonCustomObjectMapper(BatonRunner, CustomObjectMapper, metaclass=ABCMeta):
    """
    Mapper for custom objects, implemented using baton.
    """
    def _get_with_prepared_specific_query(self, specific_query: PreparedSpecificQuery, zone: str=None) \
            -> Sequence[CustomObjectType]:
        specific_query_as_baton_json = {
            BATON_SPECIFIC_QUERY_PROPERTY: PreparedSpecificQueryJSONEncoder().default(specific_query)
        }

        arguments = []
        if zone is not None:
            arguments.extend(["--zone", "%s" % zone])

        custom_objects_as_baton_json = self.run_baton_query(
                BatonBinary.BATON_SPECIFIC_QUERY, arguments, input_data=specific_query_as_baton_json)

        custom_objects = [self._object_deserialiser(custom_object_as_baton_json)
                          for custom_object_as_baton_json in custom_objects_as_baton_json]

        return custom_objects

    @abstractmethod
    def _object_deserialiser(self, object_as_json: dict) -> CustomObjectType:
        """
        Function used to take the JSON representation of the custom object returned by the specific query and produce a
        Python model.
        :param object_as_json: JSON representation of the custom object
        :return: Python model of the custom object
        """


class BatonSpecificQueryMapper(BatonCustomObjectMapper[SpecificQuery], SpecificQueryMapper):
    """
    Mapper for specific queries installed on iRODS, implemented using baton.
    """
    def get_all(self, zone: str=None) -> Sequence[SpecificQuery]:
        retrieve_query = PreparedSpecificQuery(IRODS_SPECIFIC_QUERY_LS)
        return self._get_with_prepared_specific_query(retrieve_query, zone)

    def _object_deserialiser(self, object_as_json: dict) -> SpecificQuery:
        return SpecificQueryJSONDecoder().decode_dict(object_as_json)
