from typing import Iterable, Sequence, Union

from baton._baton._baton_runner import BatonRunner
from baton.mappers import AccessControlMapper, CollectionAccessControlMapper
from baton.models import AccessControl


class BatonAccessControlMapper(BatonRunner, AccessControlMapper):
    """
    Access control mapper, implemented using baton.
    """
    def get_all(self, path: str) -> Sequence[AccessControl]:
        pass


class BatonDataObjectAccessControlMapper(BatonAccessControlMapper, AccessControlMapper):
    """
    Access control mapper for controls relating specifically to data objects, implemented using baton.
    """
    def add(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        pass

    def set(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        pass

    def remove(self, paths: Union[str, Iterable[str]], access_controls: Union[AccessControl, Iterable[AccessControl]]):
        pass


class BatonCollectionAccessControlMapper(BatonAccessControlMapper, CollectionAccessControlMapper):
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
