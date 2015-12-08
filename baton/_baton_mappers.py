from typing import List, Union

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion

from baton._baton_runner import BatonBinary
from baton._baton_runner import BatonRunner
from baton._json_to_model import baton_json_to_collection
from baton._json_to_model import baton_json_to_data_object
from baton._model_to_json import search_criteria_to_baton_json, path_to_baton_json
from baton.mappers import DataObjectMapper, CollectionMapper, IrodsEntityMapper, EntityType, EntityPathType
from baton.models import CollectionPath, DataObject


class _BatonIrodsEntityMapper(BatonRunner, IrodsEntityMapper):
    """
    Mapper for iRODS entities, implemented using baton.
    """
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria],
                    load_metadata: bool=False) -> List[EntityType]:
        if isinstance(metadata_search_criteria, SearchCriterion):
            metadata_search_criteria = SearchCriteria([metadata_search_criteria])

        baton_json = search_criteria_to_baton_json(metadata_search_criteria)
        arguments = self._create_entity_query_arguments(load_metadata)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_METAQUERY, arguments, input_data=baton_json)
        return _BatonIrodsEntityMapper._baton_json_to_irods_entities(baton_out_as_json)

    def get_by_path(self, paths: Union[EntityPathType, List[EntityPathType]], load_metadata: bool=True) \
            -> List[EntityType]:
        if not isinstance(paths, list):
            paths = [paths]
        if len(paths) == 0:
            return []

        baton_json = []
        for file in paths:
            baton_json.append(path_to_baton_json(file))
        arguments = self._create_entity_query_arguments(load_metadata)

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, arguments, input_data=baton_json)
        return _BatonIrodsEntityMapper._baton_json_to_irods_entities(baton_out_as_json)

    def _create_entity_query_arguments(self, load_metadata: bool=True) -> List[str]:
        """
        Create arguments to use with baton.
        :param load_metadata: whether baton should load metadata
        :return: the arguments to use with baton
        """
        arguments = ["--obj", "--acl", "--checksum", "--replicate", "--zone", self._irods_query_zone]
        if load_metadata:
            arguments.append("--avu")
        return arguments

    @staticmethod
    def _baton_json_to_irods_entities(entities_as_baton_json: List[dict]) -> List[EntityType]:
        """
        Converts the baton representation of multiple iRODS files to a list of `IrodsEntity` models.
        :param entities_as_baton_json: the baton json representation of the files
        :return: the equivalent models of the json represented files
        """
        assert(isinstance(entities_as_baton_json, list))

        entities = []
        for file_as_baton_json in entities_as_baton_json:
            if EntityType == DataObject:
                entity = baton_json_to_data_object(file_as_baton_json)
            else:
                entity = baton_json_to_collection(file_as_baton_json)
            entities.append(entity)

        return entities


class BatonDataObjectMapper(_BatonIrodsEntityMapper, DataObjectMapper):
    """
    TODO
    """
    def get_all_in_collection(self, collection_paths: Union[CollectionPath, List[CollectionPath]],
                              load_metadata: bool=True) -> List[DataObject]:
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

        return _BatonIrodsEntityMapper._baton_json_to_irods_entities(baton_out_as_json)


class BatonCollectionMapper(_BatonIrodsEntityMapper, CollectionMapper):
    """
    TODO
    """
    pass