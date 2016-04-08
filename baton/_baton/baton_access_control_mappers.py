from abc import ABCMeta
from typing import Iterable, Sequence, Union

from baton._baton._baton_runner import BatonRunner
from baton.mappers import AccessControlMapper, CollectionAccessControlMapper
from baton.models import AccessControl


class _BatonAccessControlMapper(BatonRunner, AccessControlMapper, metaclass=ABCMeta):
    """
    Access control mapper, implemented using baton.
    """
    def get_all(self, path: str) -> Sequence[AccessControl]:
        pass

    def add(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        pass

    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        pass

    def remove(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        pass


class BatonDataObjectAccessControlMapper(_BatonAccessControlMapper, AccessControlMapper):
    """
    Access control mapper for controls relating specifically to data objects, implemented using baton.
    """


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
