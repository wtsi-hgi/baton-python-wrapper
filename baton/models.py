from abc import ABCMeta
from datetime import datetime
from enum import Enum, unique
from typing import Iterable, List, Set
import re

import hgicommon
from hgicommon.models import Model


class Timestamped(Model, metaclass=ABCMeta):
    """
    Model that has related timestamps.
    """
    def __init__(self, created: datetime=None, last_modified: datetime=None):
        super().__init__()
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
        NONE = 0
        READ = 1
        WRITE = 2
        OWN = 3

    def __init__(self, owner: str, zone: str, level: Level):
        self.owner = owner
        self.zone = zone
        self.level = level


class IrodsEntity(Model, metaclass=ABCMeta):
    """
    Model of an entity in iRODS.
    """
    from baton.collections import IrodsMetadata
    _ABSOLUTE_PATH_REGEX = re.compile("^/.+")

    def __init__(self, path: str, access_controls: Iterable[AccessControl]=(), metadata: IrodsMetadata=None):
        if not re.match(IrodsEntity._ABSOLUTE_PATH_REGEX, path):
            raise ValueError("baton does not support the given type of relative path: \"%s\"" % path)
        self.path = path
        self._access_controls = None
        self.access_controls = access_controls
        self.metadata = metadata

    @property
    def access_controls(self) -> Set[AccessControl]:
        return self._access_controls

    @access_controls.setter
    def access_controls(self, access_controls: Iterable[AccessControl]):
        self._access_controls = set(access_controls)

    def get_collection_path(self) -> str:
        """
        Gets the path of the collection in which this entity resides.
        :return: the path of the collection that this entity is in
        """
        return self.path.rsplit('/', 1)[0]

    def get_name(self) -> str:
        """
        Gets the name of this entity.
        :return: the name of this entity
        """
        return self.path.rsplit('/', 1)[-1]


class DataObject(IrodsEntity):
    """
    Model of a data object in iRODS.
    """
    from baton.collections import IrodsMetadata

    def __init__(self, path: str, access_controls: Iterable[AccessControl]=(), metadata: IrodsMetadata=None,
                 replicas: Iterable[DataObjectReplica]=()):
        from baton.collections import DataObjectReplicaCollection
        super().__init__(path, access_controls, metadata)
        self.replicas = DataObjectReplicaCollection(replicas)


class Collection(IrodsEntity, Timestamped):
    """
    Model of a collection in iRODS.
    """
    def __init__(self, path: str, *args, **kwargs):
        path = path.rstrip("/")
        super().__init__(path, *args, **kwargs)


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
    def __init__(self, alias: str, query_arguments: List[str]=None, sql: str="(unknown)"):
        super().__init__(alias, sql)
        self.query_arguments = query_arguments if query_arguments is not None else []


# Use `SearchCriterion` from HGI common library
SearchCriterion = hgicommon.models.SearchCriterion

# Use `ComparisonOperator` from HGI common library
ComparisonOperator = hgicommon.models.ComparisonOperator
