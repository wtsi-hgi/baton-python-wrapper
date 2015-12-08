from abc import ABC, ABCMeta
from enum import Enum, unique
from typing import Sequence, Iterable, Set, TypeVar, Generic

from hgicommon.collections import Metadata
from hgicommon.models import File, Model


class Path(Model):
    """
    Model of a location of an entity in iRODS.
    """
    def __init__(self, location: str):
        self.location = location


class DataObjectPath(Path):
    """
    Model of a location to a data object in iRODS.
    """
    def get_collection_path(self) -> str:
        """
        Gets the iRODS collection that the data object belongs to.
        :return: the collection the object belongs to
        """
        return self.location.rsplit('/', 1)[0]

    def get_name(self) -> str:
        """
        Gets the name of the data object.
        :return: the name of the data object
        """
        return self.location.rsplit('/', 1)[-1]


class CollectionPath(Path):
    """
    Model of a location to a collection in iRODS.
    """
    pass


EntityPathType = TypeVar('S', DataObjectPath, CollectionPath)


class DataObjectReplica(Model):
    """
    Model of a file replicate in iRODS.
    """
    def __init__(self, id: int, checksum: str):
        self.id = id
        self.checksum = checksum


class IrodsMetadata(Metadata):
    """
    iRODS metadata is in the form of "AVUs" (attribute-value-unit tuples). Attributes may have many values therefore all
    attributes are a sets.

    Units are no currently considered.
    """
    def set(self, key: str, value: Set[str]):
        assert isinstance(value, set)
        super().set(key, value)

    def get(self, attribute: str, default=None) -> Set[str]:
        value = super().get(attribute, default)
        assert isinstance(value, set)
        return value


class AccessControl(Model):
    """
    Model of an iRODS Access Control item (from an ACL).
    """
    @unique
    class Level(Enum):
        READ = 0
        WRITE = 1
        OWN = 2

    def __init__(self, owner: str, zone: str, level: Level):
        self.owner = owner
        self.zone = zone
        self.level = level


# XXX: Not using generics here for path type as their current level of support is terrible.
class IrodsEntity(Model):
    """
    Model of an entity in iRODS.
    """
    def __init__(self, path: Path, access_control_list: Iterable[AccessControl],
                 metadata: Iterable[IrodsMetadata]=None):
        self.path = path
        self.acl = access_control_list
        self.metadata = metadata


class DataObject(IrodsEntity):
    """
    Model of a data object in iRODS.
    """
    def __init__(self, path: DataObjectPath, checksum: str, access_control_list: Iterable[AccessControl],
                 metadata: Iterable[IrodsMetadata] = None, replicas: Iterable[DataObjectReplica] = ()):
        super().__init__(path, access_control_list, metadata)
        self.checksum = checksum
        self.replicas = replicas

    def get_invalid_replicas(self) -> Sequence[DataObjectReplica]:
        """
        Gets the replicates that have checksums that do not match that of the "original" file and which should
        subsequently be regarded as invalid.
        :return: list of invalid replicas
        """
        invalid_replicas = []
        for replica in self.replicas:
            if replica.checksum != self.checksum:
                invalid_replicas.append(replica)
        return invalid_replicas


class Collection(IrodsEntity):
    """
    Model of a collection in iRODS.
    """
    def __init__(self, path: CollectionPath, access_control_list: Iterable[AccessControl],
                 metadata: Iterable[IrodsMetadata] = None):
        super().__init__(path, access_control_list, metadata)


EntityType = TypeVar('T', DataObject, Collection)
