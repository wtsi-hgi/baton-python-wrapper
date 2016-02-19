from abc import ABCMeta
from datetime import datetime
from enum import Enum, unique
from typing import Iterable, List

from hgicommon.models import Model


class Timestamped(Model, metaclass=ABCMeta):
    """
    Model that has related timestamps.
    """
    def __init__(self, created: datetime=None, last_modified: datetime=None):
        self.created = created
        self.last_modified = last_modified


class DataObjectReplica(Timestamped):
    """
    Model of a file replicate in iRODS.
    """
    def __init__(self, number: int, checksum: str, host: str=None, resource_name: str=None, up_to_date: bool=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = number
        self.checksum = checksum
        self.host = host
        self.resource_name = resource_name
        self.up_to_date = up_to_date


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
    from baton.collections import IrodsMetadata

    def __init__(self, path: str, access_control_list: Iterable[AccessControl]=None, metadata: IrodsMetadata=None):
        self.path = path
        self.acl = access_control_list
        self.metadata = metadata


class DataObject(IrodsEntity):
    """
    Model of a data object in iRODS.
    """
    from baton.collections import IrodsMetadata

    def __init__(self, replicas: Iterable[DataObjectReplica]=(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        from baton.collections import DataObjectReplicaCollection
        self.replicas = DataObjectReplicaCollection(replicas)

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


class Collection(IrodsEntity, Timestamped):
    """
    Model of a collection in iRODS.
    """


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
    def __init__(self, alias: str, query_arguments: List[str]=None, sql: str= "(unknown)"):
        super().__init__(alias, sql)
        self.query_arguments = query_arguments if query_arguments is not None else []
