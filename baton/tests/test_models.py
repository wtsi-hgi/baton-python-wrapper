import unittest

from baton import IrodsFile
from baton.models import IrodsFileReplica


class TestIrodsFile(unittest.TestCase):
    """
    Tets for `IrodsFile`.
    """
    _DIRECTORY = "/test"
    _FILENAME = "myFile"
    _CHECKSUMS = ["2c558824f250de9d55c07600291f4272", "2c558824f250de9d55c07600291f4233", "2c558824f250de9d55c07600291f4257"]

    def test_init_with_duplicate_id_replicates(self):
        replicas = [IrodsFileReplica(1, "") for _ in range(10)]
        self.assertRaises(ValueError, IrodsFile, TestIrodsFile._DIRECTORY, TestIrodsFile._FILENAME,
                          TestIrodsFile._CHECKSUMS[0], replicas)

    def test_get_invalid_replica_with_no_replicas(self):
        irods_file = IrodsFile(TestIrodsFile._DIRECTORY, TestIrodsFile._FILENAME, TestIrodsFile._CHECKSUMS[0], [])

        self.assertCountEqual(irods_file.get_invalid_replica(), [])

    def test_get_invalid_replica_with_no_valid_replicas(self):
        replicas = [IrodsFileReplica(1, TestIrodsFile._CHECKSUMS[1]), IrodsFileReplica(2, TestIrodsFile._CHECKSUMS[2])]
        irods_file = IrodsFile(TestIrodsFile._DIRECTORY, TestIrodsFile._FILENAME, TestIrodsFile._CHECKSUMS[0], replicas)

        self.assertCountEqual(irods_file.get_invalid_replica(), replicas)

    def test_get_invalid_replica_with_all_valid_replicas(self):
        replicas = []
        for i in range(10):
            replicas.append(IrodsFileReplica(i, TestIrodsFile._CHECKSUMS[0]))
        irods_file = IrodsFile(TestIrodsFile._DIRECTORY, TestIrodsFile._FILENAME, TestIrodsFile._CHECKSUMS[0], replicas)

        self.assertCountEqual(irods_file.get_invalid_replica(), [])

    def test_get_invalid_replica_with_mixed_valid_replicas(self):
        replicas = []
        for i in range(len(TestIrodsFile._CHECKSUMS)):
            replicas.append(IrodsFileReplica(i, TestIrodsFile._CHECKSUMS[i]))

        irods_file = IrodsFile(TestIrodsFile._DIRECTORY, TestIrodsFile._FILENAME, TestIrodsFile._CHECKSUMS[0], replicas)

        self.assertCountEqual(irods_file.get_invalid_replica(), replicas[1:])
