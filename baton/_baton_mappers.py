from abc import ABCMeta, abstractmethod
from typing import Union, Sequence, List

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion

from baton._baton_runner import BatonBinary, BatonRunner
from baton._json_to_model import baton_json_to_collection,baton_json_to_data_object
from baton._model_to_json import search_criteria_to_baton_json, data_object_to_baton_json, \
    collection_to_baton_json, prepared_specific_query_to_baton_json
from baton.mappers import DataObjectMapper, CollectionMapper, IrodsEntityMapper, EntityType, CustomObjectType, \
    CustomObjectMapper, SpecificQueryMapper
from baton.models import DataObject, Collection, PreparedSpecificQuery, SpecificQuery


class _BatonIrodsEntityMapper(BatonRunner, IrodsEntityMapper, metaclass=ABCMeta):
    """
    Mapper for iRODS entities, implemented using baton.
    """
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria],
                    load_metadata: bool=True) -> Sequence[EntityType]:
        if isinstance(metadata_search_criteria, SearchCriterion):
            metadata_search_criteria = SearchCriteria([metadata_search_criteria])

        baton_json = search_criteria_to_baton_json(metadata_search_criteria)
        arguments = self._create_entity_query_arguments(load_metadata)

        # TODO: "--obj" limits search to object metadata only and "--coll" for collections

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_METAQUERY, arguments, input_data=baton_json)
        return self._baton_json_to_irods_entities(baton_out_as_json)

    def get_by_path(self, paths: Union[str, Sequence[str]], load_metadata: bool=True) -> Sequence[EntityType]:
        if not isinstance(paths, list):
            paths = [paths]
        if len(paths) == 0:
            return []

        baton_json = []
        for path in paths:
            baton_json.append(self._path_to_baton_json(path))
        arguments = self._create_entity_query_arguments(load_metadata)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)
        return self._baton_json_to_irods_entities(baton_out_as_json)

    def _create_entity_query_arguments(self, load_metadata: bool=True) -> List[str]:
        """
        Create arguments to use with baton.
        :param load_metadata: whether baton should load metadata
        :return: the arguments to use with baton
        """
        arguments = ["--acl", "--replicate", "--zone", self._irods_query_zone]
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
        pass

    @abstractmethod
    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> EntityType:
        """
        Converts the baton representation of an iRODS entity to a list of `EntityType` models.
        :param entity_as_baton_json: the baton serialization representation of the entity
        :return: the equivalent models
        """
        pass


class BatonDataObjectMapper(_BatonIrodsEntityMapper, DataObjectMapper):
    """
    iRODS data object mapper, implemented using baton.
    """
    def get_all_in_collection(self, collection_paths: Union[str, Sequence[str]], load_metadata: bool=True) \
            -> Sequence[DataObject]:
        if not isinstance(collection_paths, list):
            collection_paths = [collection_paths]
        if len(collection_paths) == 0:
            return []

        baton_json = []
        for path in collection_paths:
            collection = Collection(path)
            baton_json.append(collection_to_baton_json(collection))
        arguments = self._create_entity_query_arguments(load_metadata)
        arguments.append("--contents")

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)

        data_objects_as_baton_json = []
        for baton_item_as_json in baton_out_as_json:
            # TODO: Remove hard-coded JSON property name
            data_objects_as_baton_json += baton_item_as_json["contents"]

        return self._baton_json_to_irods_entities(data_objects_as_baton_json)

    def _path_to_baton_json(self, path: str) -> dict:
        data_object = DataObject(path)
        return data_object_to_baton_json(data_object)

    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> DataObject:
        return baton_json_to_data_object(entity_as_baton_json)


class BatonCollectionMapper(_BatonIrodsEntityMapper, CollectionMapper):
    """
    iRODS collection mapper, implemented using baton.
    """
    def _path_to_baton_json(self, path: str) -> dict:
        collection = Collection(path)
        return collection_to_baton_json(collection)

    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> Collection:
        return baton_json_to_collection(entity_as_baton_json)


class BatonCustomObjectMapper(BatonRunner, CustomObjectMapper, metaclass=ABCMeta):
    """
    Mapper for custom objects, implemented using baton.
    """
    def _get_with_prepared_specific_query(self, specific_query: PreparedSpecificQuery) -> Sequence[CustomObjectType]:
        specific_query_as_baton_json = prepared_specific_query_to_baton_json(specific_query)

        custom_objects_as_baton_json = self.run_baton_query(
                BatonBinary.BATON_SPECIFIC_QUERY, input_data=specific_query_as_baton_json)

        custom_objects = [self._object_serialiser(custom_object_as_baton_json)
                          for custom_object_as_baton_json in custom_objects_as_baton_json]

        return custom_objects

    @abstractmethod
    def _object_serialiser(self, object_as_json: dict) -> CustomObjectType:
        """
        Function used to take the JSON representation of the custom object returned by the specific query and produce a
        model.
        :param object_as_json: JSON representation of the custom object
        :return: Python model of the custom object
        """
        pass


class BatonSpecificQueryMapper(BatonCustomObjectMapper[SpecificQuery], SpecificQueryMapper):
    """
    Mapper for specific queries installed on iRODS, implemented using baton.
    """
    def get_all(self) -> Sequence[SpecificQuery]:
        retrieve_query = PreparedSpecificQuery("ls")
        return self._get_with_prepared_specific_query(retrieve_query)

    def _object_serialiser(self, object_as_json: dict) -> SpecificQuery:
        # TODO: Strings -> Constants (probably should move to _json_to_model.py)
        return SpecificQuery(
            object_as_json["alias"],
            object_as_json["sqlStr"]
        )
