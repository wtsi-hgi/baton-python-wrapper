from abc import ABCMeta, abstractmethod
from typing import List, Union

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion

from baton._baton_runner import BatonBinary
from baton._baton_runner import BatonRunner
from baton._json_to_model import baton_json_to_collection
from baton._json_to_model import baton_json_to_data_object
from baton._model_to_json import search_criteria_to_baton_json, path_to_baton_json
from baton.mappers import DataObjectMapper, CollectionMapper, IrodsEntityMapper, EntityType
from baton.models import CollectionPath, DataObject, Collection, DataObjectPath


class _BatonIrodsEntityMapper(BatonRunner, IrodsEntityMapper, metaclass=ABCMeta):
    """
    Mapper for iRODS entities, implemented using baton.
    """
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria],
                    load_metadata: bool=True) -> List[EntityType]:
        if isinstance(metadata_search_criteria, SearchCriterion):
            metadata_search_criteria = SearchCriteria([metadata_search_criteria])

        baton_json = search_criteria_to_baton_json(metadata_search_criteria)
        arguments = self._create_entity_query_arguments(load_metadata)

        # TODO: "--obj" limits search to object metadata only and "--coll" for collections

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_METAQUERY, arguments, input_data=baton_json)
        return self._baton_json_to_irods_entities(baton_out_as_json)

    def get_by_path(self, paths: Union[str, List[str]], load_metadata: bool=True) -> List[EntityType]:
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
        arguments = ["--acl", "--checksum", "--replicate", "--zone", self._irods_query_zone]
        if load_metadata:
            arguments.append("--avu")
        return arguments

    @abstractmethod
    def _path_to_baton_json(self, path: str) -> dict:
        """
        TODO
        :param path:
        :return:
        """
        pass

    @abstractmethod
    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> EntityType:
        """
        Converts the baton representation of an iRODS entity to a list of `EntityType` models.
        :param entity_as_baton_json: the baton json representation of the entity
        :return: the equivalent models
        """
        pass

    def _baton_json_to_irods_entities(self, entities_as_baton_json: List[dict]) -> List[EntityType]:
        """
        Converts the baton representation of multiple iRODS entities to a list of `EntityType` models.
        :param entities_as_baton_json: the baton json representation of the entities
        :return: the equivalent models
        """
        assert(isinstance(entities_as_baton_json, list))

        entities = []
        for file_as_baton_json in entities_as_baton_json:
            entity = self._baton_json_to_irod_entity(file_as_baton_json)
            entities.append(entity)

        return entities


class BatonDataObjectMapper(_BatonIrodsEntityMapper, DataObjectMapper):
    """
    TODO
    """
    def get_all_in_collection(self, collection_paths: Union[str, List[str]], load_metadata: bool=True) \
            -> List[DataObject]:
        if not isinstance(collection_paths, list):
            collection_paths = [collection_paths]
        if len(collection_paths) == 0:
            return []

        baton_json = []
        for path in collection_paths:
            baton_json.append(path_to_baton_json(path))
        arguments = self._create_entity_query_arguments(load_metadata)
        arguments.append("--contents")

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)

        files_as_baton_json = []
        for baton_item_as_json in baton_out_as_json:
            files_as_baton_json += baton_item_as_json["contents"]

        return self._baton_json_to_irods_entities(baton_out_as_json)

    def _path_to_baton_json(self, path: str) -> dict:
        path_as_model = DataObjectPath(path)
        return path_to_baton_json(path_as_model)

    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> DataObject:
        return baton_json_to_data_object(entity_as_baton_json)


class BatonCollectionMapper(_BatonIrodsEntityMapper, CollectionMapper):
    """
    TODO
    """
    def _path_to_baton_json(self, path: str) -> dict:
        path_as_model = CollectionPath(path)
        return path_to_baton_json(path_as_model)

    def _baton_json_to_irod_entity(self, entity_as_baton_json: dict) -> Collection:
        return baton_json_to_collection(entity_as_baton_json)