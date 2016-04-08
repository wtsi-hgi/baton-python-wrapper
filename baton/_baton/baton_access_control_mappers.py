from abc import ABCMeta, abstractmethod
from typing import Iterable, Sequence, Union, Dict, List

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton._constants import BATON_ACL_PROPERTY
from baton._baton.json import DataObjectJSONEncoder, AccessControlJSONDecoder, CollectionJSONEncoder
from baton.mappers import AccessControlMapper, CollectionAccessControlMapper
from baton.models import AccessControl, DataObject, IrodsEntity, Collection


class _BatonAccessControlMapper(BatonRunner, AccessControlMapper, metaclass=ABCMeta):
    """
    Access control mapper, implemented using baton.
    """
    _ACCESS_CONTROL_JSON_ENCODER = AccessControlJSONDecoder()

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

    def get_all(self, path: str) -> Sequence[AccessControl]:
        baton_json = self._path_to_baton_json(path)
        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, ["--acl"], input_data=baton_json)
        assert len(baton_out_as_json) == 1
        access_controls_as_baton_json = baton_out_as_json[0][BATON_ACL_PROPERTY]
        return _BatonAccessControlMapper._ACCESS_CONTROL_JSON_ENCODER.decode_parsed(access_controls_as_baton_json)

    def add(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(access_controls, AccessControl):
            access_controls = [access_controls]

        baton_json = []
        for path in paths:
            entity = self._create_entity_with_path(path)
            # TODO: This is inefficient - `get_all` should accept a list then this could be done in one call, not n
            entity.acl = set(self.get_all(path)).union(set(access_controls))
            baton_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_json)

    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(access_controls, AccessControl):
            access_controls = [AccessControl]

        baton_json = []
        for path in paths:
            entity = self._create_entity_with_path(path)
            entity.acl = access_controls
            baton_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_json)

    def remove(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(access_controls, AccessControl):
            access_controls = [AccessControl]

        baton_json = []
        for path in paths:
            entity = self._create_entity_with_path(path)
            # TODO: This is inefficient - `get_all` should accept a list then this could be done in one call, not n
            entity.acl = set(self.get_all(path)) - set(access_controls)
            baton_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_json)

    def _path_to_baton_json(self, path: str) -> Dict:
        """
        Converts a path to the type of iRODS entity the mapper deals with, to its JSON representation.
        :param path: the path to convert
        :return: the JSON representation of the path
        """
        entity = self._create_entity_with_path(path)
        return self._entity_to_baton_json(entity)


class BatonDataObjectAccessControlMapper(_BatonAccessControlMapper, AccessControlMapper):
    """
    Access control mapper for controls relating specifically to data objects, implemented using baton.
    """
    def _create_entity_with_path(self, path: str) -> DataObject:
        return DataObject(path)

    def _entity_to_baton_json(self, entity: DataObject) -> Dict:
        return DataObjectJSONEncoder().default(entity)


class BatonCollectionAccessControlMapper(_BatonAccessControlMapper, CollectionAccessControlMapper):
    """
    Access control mapper for controls relating specifically to collections, implemented using baton.
    """
    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]],
            recursive: bool = False):
        pass

    def add(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]],
            recursive: bool = False):
        pass

    def remove(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]],
               recursive: bool = False):
        pass

    def _create_entity_with_path(self, path: str) -> DataObject:
        return Collection(path)

    def _entity_to_baton_json(self, entity: Collection) -> Dict:
        return CollectionJSONEncoder().default(entity)
