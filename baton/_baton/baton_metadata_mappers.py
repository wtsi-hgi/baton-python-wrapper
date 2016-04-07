from abc import ABCMeta, abstractmethod
from typing import Dict

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton._constants import BATON_METAMOD_ADD_OPERATION, BATON_AVU_PROPERTY
from baton._baton._constants import BATON_METAMOD_REMOVE_OPERATION
from baton._baton.json import DataObjectJSONEncoder, CollectionJSONEncoder, IrodsMetadataJSONDecoder
from baton.collections import IrodsMetadata
from baton.mappers import IrodsMetadataMapper
from baton.models import DataObject, Collection, IrodsEntity


class _BatonIrodsMetadataMapper(BatonRunner, IrodsMetadataMapper, metaclass=ABCMeta):
    """
    iRODS metadata mapper, implemented using baton.
    """
    _IRODS_METADATA_JSON_ENCODER = IrodsMetadataJSONDecoder()

    def get_all(self, path: str) -> IrodsMetadata:
        baton_json = self._path_to_baton_json(path)
        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, ["--avu"], input_data=baton_json)
        assert len(baton_out_as_json) == 1
        metadata_as_baton_json = baton_out_as_json[0][BATON_AVU_PROPERTY]
        return _BatonIrodsMetadataMapper._IRODS_METADATA_JSON_ENCODER.decode_dict(metadata_as_baton_json)

    def set(self, path: str, metadata: IrodsMetadata):
        # baton does not support "set" natively, therefore this operation is not transactional
        existing_metadata = self.get_all(path)
        self.remove(path, existing_metadata)
        self.add(path, metadata)

    def add(self, path: str, metadata: IrodsMetadata):
        self._modify(path, metadata, BATON_METAMOD_ADD_OPERATION)

    def remove(self, path: str, metadata: IrodsMetadata):
        self._modify(path, metadata, BATON_METAMOD_REMOVE_OPERATION)

    def remove_all(self, path: str):
        self.set(path, IrodsMetadata())

    @abstractmethod
    def _create_entity_with_path(self, path: str) -> IrodsEntity:
        """
        Creates an entity model with the given path.
        :param path: the path the entity should have
        :return: the created entity model
        """

    @abstractmethod
    def _entity_to_baton_json(self, entity: IrodsEntity) -> Dict:
        """
        Converts an entity model to its baton JSON representation.
        :param entity: the entity to produce the JSON representation of
        :return: the JSON representation
        """

    def _path_to_baton_json(self, path: str) -> Dict:
        """
        Converts a path to the type of iRODS entity the mapper deals with, to its JSON representation.
        :param path: the path to convert
        :return: the JSON representation of the path
        """
        entity = self._create_entity_with_path(path)
        return self._entity_to_baton_json(entity)

    def _modify(self, path: str, metadata: IrodsMetadata, operation: str):
        """
        Modifies the metadata of the entity in iRODS with the given path.
        :param path: the path of the entity to modify
        :param metadata: the metadata to change
        :param operation: the baton operation used to modify the metadata
        """
        entity = self._create_entity_with_path(path)
        entity.metadata = metadata
        baton_json = self._entity_to_baton_json(entity)
        arguments = ["--operation", operation]
        self.run_baton_query(BatonBinary.BATON_METAMOD, arguments, input_data=baton_json)


class BatonDataObjectIrodsMetadataMapper(_BatonIrodsMetadataMapper):
    """
    iRODS data object metadata mapper, implemented using baton.
    """
    def _create_entity_with_path(self, path: str) -> DataObject:
        return DataObject(path)

    def _entity_to_baton_json(self, entity: DataObject) -> Dict:
        return DataObjectJSONEncoder().default(entity)


class BatonCollectionIrodsMetadataMapper(_BatonIrodsMetadataMapper):
    """
    iRODS collection metadata mapper, implemented using baton.
    """
    def _create_entity_with_path(self, path: str) -> DataObject:
        return Collection(path)

    def _entity_to_baton_json(self, entity: Collection) -> Dict:
        return CollectionJSONEncoder().default(entity)
