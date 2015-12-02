import copy
from enum import Enum, unique
from typing import List, Sequence, Iterable, Set

from hgicommon.collections import Metadata
from hgicommon.models import File, Model


class IrodsFileReplica(Model):
    """
    Model of a file replicate in iRODS.
    """
    def __init__(self, id: int, checksum: str):
        self.id = id
        self.checksum = checksum


class IrodsFile(File):
    """
    Model of a file in iRODS.
    """
    def __init__(self, directory: str, file_name: str, checksum: str, replicas: Iterable[IrodsFileReplica]):
        super(IrodsFile, self).__init__(directory, file_name)
        self.checksum = checksum
        self.replicas = set()
        for replica in replicas:
            if replica in self.replicas:
                raise ValueError("Replicate with duplicate ID given: %s" % replica)
            self.replicas.add(replica)

    def get_invalid_replica(self) -> Sequence[IrodsFileReplica]:
        invalid_replica = []
        for replica in self.replicas:
            if replica.checksum != self.checksum:
                invalid_replica.append(replica)
        return invalid_replica


class IrodsMetadata(Metadata):
    """
    iRODS metadata is in the form of "AVUs" (attribute-value-unit tuples). Attributes may have many values therefore all
    attributes are a list.

    Units are no currently considered.
    """
    def set(self, key: str, value: List[str]):
        canonical_value = sorted(set(value)) if type(value) is list else [value]
        super().set(key, canonical_value)


class IrodsAccessControlList:
    """
    Model of an iRODS Access Control List (ACL).
    """
    @unique
    class Permission(Enum):
        READ = 0
        OWN = 1

    def __init__(self, owner: str, zone: str, permission: str):
        self.owner = owner
        self.zone = zone
        self.permission = permission