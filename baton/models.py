from hgicommon.models import File
from typing import List


class IrodsFile(File):
    """
    Model of a file in iRODS.
    """
    def __init__(self, directory: str, file_name: str, checksum: str, replica_checksums: List[str]):
        super(IrodsFile, self).__init__(directory, file_name)
        self.checksum = checksum
        self.replica_checksums = replica_checksums
