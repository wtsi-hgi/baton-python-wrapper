from abc import ABCMeta, abstractmethod
from typing import Iterable, Sequence, Union, Dict, List, Set

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton._constants import BATON_ACL_PROPERTY
from baton._baton.json import DataObjectJSONEncoder, AccessControlJSONDecoder, CollectionJSONEncoder, \
    AccessControlSetJSONDecoder
from baton.mappers import AccessControlMapper, CollectionAccessControlMapper
from baton.models import AccessControl, DataObject, IrodsEntity, Collection


class _BatonAccessControlMapper(BatonRunner, AccessControlMapper, metaclass=ABCMeta):
    """
    Access control mapper, implemented using baton.
    """
    _ACCESS_CONTROL_SET_JSON_ENCODER = AccessControlSetJSONDecoder()

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

    def get_all(self, paths: Union[str, Sequence[str]]) -> Union[Set[AccessControl], Sequence[Set[AccessControl]]]:
        if len(paths) == 0:
            return set()
        if isinstance(paths, str):
            single_path = True
            paths = [paths]
        else:
            single_path = False

        baton_json = []
        for path in paths:
            baton_json.append(self._path_to_baton_json(path))

        baton_out_as_json = self.run_baton_query(BatonBinary.BATON_LIST, ["--acl"], input_data=baton_json)
        assert len(baton_out_as_json) == len(paths)

        access_controls_for_paths = []
        for entity_as_baton_json in baton_out_as_json:
            access_controls_as_baton_json = entity_as_baton_json[BATON_ACL_PROPERTY]
            access_contorls = _BatonAccessControlMapper._ACCESS_CONTROL_SET_JSON_ENCODER.decode_parsed(
                access_controls_as_baton_json)
            access_controls_for_paths.append(access_contorls)

        return access_controls_for_paths[0] if single_path else access_controls_for_paths


    def add_or_replace(self, paths: Union[str, Iterable[str]],
                       access_controls: Union[AccessControl, Iterable[AccessControl]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(access_controls, AccessControl):
            access_controls = [access_controls]

        baton_json = []
        for path in paths:
            entity = self._create_entity_with_path(path)
            entity.access_controls = access_controls
            baton_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_json)

    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(access_controls, AccessControl):
            access_controls = [access_controls]

        # baton-chmod does a mix of set and add: if no level has been defined for a user, else sets if it has
        # Taking easiest route of starting from a blank slate
        self.revoke_all(paths)

        baton_json = []
        for path in paths:
            entity = self._create_entity_with_path(path)
            entity.access_controls = access_controls
            baton_json.append(self._entity_to_baton_json(entity))
        self.run_baton_query(BatonBinary.BATON_CHMOD, input_data=baton_json)

    def revoke(self, paths: Union[str, Iterable[str]], users_or_groups: Union[str, Iterable[str]]):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(users_or_groups, str):
            users_or_groups = [users_or_groups]

        no_access_controls = [AccessControl(users_or_group, AccessControl.Level.NONE) for users_or_group in users_or_groups]
        self.add_or_replace(paths, no_access_controls)

    def revoke_all(self, paths: Union[str, Iterable[str]]):
        if isinstance(paths, str):
            paths = [paths]

        baton_json = []
        for path in paths:
            # TODO: This is inefficient - `get_all` should accept a list then this could be done in one call, not n
            access_controls = self.get_all(path)
            for access_control in access_controls:
                access_control.level = AccessControl.Level.NONE
            entity = self._create_entity_with_path(path)
            entity.access_controls = access_controls
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
            recursive: bool=False):
        if recursive:
            raise NotImplementedError()
        else:
            super().set(paths, access_controls)

    def add_or_replace(self, paths: Union[str, Iterable[str]],
                       access_controls: Union[AccessControl, Iterable[AccessControl]], recursive: bool=False):
        if recursive:
            raise NotImplementedError()
        else:
            super().add_or_replace(paths, access_controls)

    def revoke(self, paths: Union[str, Iterable[str]], users_or_groups: Union[str, Iterable[str]],
               recursive: bool=False):
        if recursive:
            raise NotImplementedError()
        else:
            super().revoke(paths, users_or_groups)

    def revoke_all(self, paths: Union[str, Iterable[str]], recursive: bool=False):
        if recursive:
            raise NotImplementedError()
        else:
            super().revoke_all(paths)

    # def run_baton_query(self):

    def _create_entity_with_path(self, path: str) -> DataObject:
        return Collection(path)

    def _entity_to_baton_json(self, entity: Collection) -> Dict:
        return CollectionJSONEncoder().default(entity)
