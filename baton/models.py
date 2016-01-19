from abc import ABCMeta
from enum import Enum, unique
from typing import Iterable, Set, List

from hgicommon.collections import Metadata
from hgicommon.models import Model


class DataObjectReplica(Model):
    """
    Model of a file replicate in iRODS.
    """
    def __init__(self, number: int, checksum: str, host: str=None, resource_name: str=None, up_to_date: bool=None):
        self.number = number
        self.checksum = checksum
        self.host = host
        self.resource_name = resource_name
        self.up_to_date = up_to_date


class IrodsMetadata(Metadata):
    """
    iRODS metadata is in the form of "AVUs" (attribute-value-unit tuples). Attributes may have many values therefore all
    attributes are a sets.

    Units are no currently considered.
    """
    def get(self, key: str, default=None) -> Set[str]:
        value = super().get(key, default)
        assert isinstance(value, set)
        return value

    def __getitem__(self, key: str) -> Set[str]:
        value = super().__getitem__(key)
        assert isinstance(value, set)
        return value

    def __setitem__(self, key: str, value: Set[str]):
        assert isinstance(value, set)
        super().__setitem__(key, value)


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


class IrodsEntity(Model, metaclass=ABCMeta):
    """
    Model of an entity in iRODS.
    """
    def __init__(self, path: str, access_control_list: Iterable[AccessControl]=None, metadata: IrodsMetadata=None):
        self.path = path
        self.acl = access_control_list
        self.metadata = metadata


class DataObject(IrodsEntity):
    """
    Model of a data object in iRODS.
    """
    def __init__(self, path: str, access_control_list: Iterable[AccessControl]=None,
                 metadata: Iterable[IrodsMetadata]=None, replicas: Iterable[DataObjectReplica]=()):
        super().__init__(path, access_control_list, metadata)
        self.replicas = replicas

    def get_collection_path(self) -> str:
        """
        Gets the path of the collection in which this data object resides.
        :return: the path of the collection that the data object is in
        """
        return self.path.rsplit('/', 1)[0]

    def get_name(self) -> str:
        """
        Gets the name of this data object.
        :return: the name of the data object
        """
        return self.path.rsplit('/', 1)[-1]


class Collection(IrodsEntity):
    """
    Model of a collection in iRODS.
    """
    pass


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
    def __init__(self, alias: str, arguments: List[str]=None, sql: str="(unknown)"):
        super().__init__(alias, sql)
        self.query_arguments = arguments if arguments is not None else []
