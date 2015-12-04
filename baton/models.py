from enum import Enum, unique
from typing import Sequence, Iterable, Set

from hgicommon.collections import Metadata
from hgicommon.models import File, Model


class IrodsFileReplica(Model):
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
        assert isinstance(value, set) or value == default
        return value


class IrodsAccessControl(Model):
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


class IrodsFile(File):
    """
    Model of a file in iRODS.
    """
    def __init__(self, directory: str, file_name: str, checksum: str, access_control_list: Iterable[IrodsAccessControl],
                 replicas: Iterable[IrodsFileReplica]=(), metadata: Iterable[IrodsMetadata]=None):
        super(IrodsFile, self).__init__(directory, file_name)
        self.checksum = checksum
        self.acl = access_control_list
        self.replicas = replicas
        self.metadata = metadata

    def get_invalid_replicas(self) -> Sequence[IrodsFileReplica]:
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

    def cast_to_file(self) -> File:
        """
        Casts this model of an iRODS file to a `File` model.
        :return: `File` representation of this model
        """
        return File(self.directory, self.file_name)
