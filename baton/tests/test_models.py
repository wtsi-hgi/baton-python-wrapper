import copy
import unittest

from baton.models import DataObject, IrodsMetadata

_COLLECTION = "/collection/sub_collection"
_FILE_NAME = "file_name"
_CHECKSUMS = ["2c558824f250de9d55c07600291f4272", "2c558824f250de9d55c07600291f4233", "2c558824f250de9d55c07600291f4257"]


class TestDataObject(unittest.TestCase):
    """
    Tests for `DataObject`.
    """
    def setUp(self):
        self.data_object = DataObject("%s/%s" % (_COLLECTION, _FILE_NAME), _CHECKSUMS[0], [], [])

    def test_get_collection_path(self):
        self.assertEquals(self.data_object.get_collection_path(), _COLLECTION)

    def test_get_name(self):
        self.assertEquals(self.data_object.get_name(), _FILE_NAME)

    def test_equality(self):
        data_object_2 = copy.deepcopy(self.data_object)
        self.assertEqual(data_object_2, self.data_object)


if __name__ == "__main__":
    unittest.main()
