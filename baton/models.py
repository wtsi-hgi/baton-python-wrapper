from hgicommon.collections import Metadata
from hgicommon.models import File
from typing import List, Sequence, Optional


class IrodsFile(File):
    """
    Model of a file in iRODS.
    """
    def __init__(self, directory: str, file_name: str, checksum: str, replica_checksums: List[str]):
        super(IrodsFile, self).__init__(directory, file_name)
        self.checksum = checksum
        self.replica_checksums = replica_checksums


class IrodsMetadata(Metadata):
    """
    IRODS metadata is in the form of "AVUs" (attribute-value-unit tuples). Attributes may have many values therefore all
    attributes are a list.

    Units are no currently considered.
    """
    def set(self, key: str, value: List[str]):
        canonical_value = sorted(set(value)) if type(value) is list else [value]
        super().set(key, canonical_value)
