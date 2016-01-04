from enum import Enum, unique
from typing import Sequence, Iterable, Set, TypeVar, List, Any

from hgicommon.collections import Metadata
from hgicommon.models import Model


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


class IrodsEntity(Model):
    """
    Model of an entity in iRODS.
    """
    def __init__(self, path: str, access_control_list: Iterable[AccessControl] = None,
                 metadata: Iterable[IrodsMetadata] = None):
        self.path = path
        self.acl = access_control_list
        self.metadata = metadata


class DataObject(IrodsEntity):
    """
    Model of a data object in iRODS.
    """
    def __init__(self, path: str, checksum: str = None, access_control_list: Iterable[AccessControl]=None,
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

    def get_directory(self) -> str:
        """
        Gets the directory of this data object.
        :return: the directory that the data object is in
        """
        return self.path.rsplit('/', 1)[0]

    def get_name(self) -> str:
        """
        Gets the name of this data object.
        :param data_object_path: the path of the data object
        :return: the name of the data object
        """
        return self.path.rsplit('/', 1)[-1]


class Collection(IrodsEntity):
    """
    Model of a collection in iRODS.
    """
    def __init__(self, path: str, access_control_list: Iterable[AccessControl] = None,
                 metadata: Iterable[IrodsMetadata] = None):
        super().__init__(path, access_control_list, metadata)


class SpecificQuery(Model):
    """
    Model of a query installed on iRODS.
    """
    def __init__(self, alias: str, sql: str):
        self.alias = alias
        self.sql = sql

    def get_number_of_arguments(self) -> int:
        """
        Gets the number of a arguments in the specific query.
        :return: the number of arguments
        """
        return self.sql.count("?")


class PreparedSpecificQuery(SpecificQuery):
    """
    Model of a prepared specific query.
    """
    def __init__(self, alias: str, arguments: List[Any] = None, sql: str= "unknown"):
        super().__init__(alias, sql)
        self.query_arguments = arguments if arguments is not None else []
