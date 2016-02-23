import copy
import unittest

from baton.models import DataObject, SpecificQuery

_COLLECTION = "/collection/sub_collection"
_FILE_NAME = "file_name"
_CHECKSUMS = ["2c558824f250de9d55c07600291f4272", "2c558824f250de9d55c07600291f4233", "2c558824f250de9d55c07600291f4257"]


class TestDataObject(unittest.TestCase):
    """
    Tests for `DataObject`.
    """
    def setUp(self):
        self.data_object = DataObject("%s/%s" % (_COLLECTION, _FILE_NAME))

    def test_get_collection_path(self):
        self.assertEquals(self.data_object.get_collection_path(), _COLLECTION)

    def test_get_name(self):
        self.assertEquals(self.data_object.get_name(), _FILE_NAME)

    def test_equality(self):
        data_object_2 = copy.deepcopy(self.data_object)
        self.assertEqual(data_object_2, self.data_object)


class TestSpecificQuery(unittest.TestCase):
    """
    Tests for `SpecificQuery`.
    """
    def test_get_number_of_arguments_when_none(self):
        specific_query = SpecificQuery("alias", "SELECT * FROM Table")
        self.assertEqual(specific_query.get_number_of_arguments(), 0)

    def test_get_number_of_arguments_when_many(self):
        specific_query = SpecificQuery("alias", "SELECT * FROM Table WHERE Table.a = ? AND Table.b LIKE ?")
        self.assertEqual(specific_query.get_number_of_arguments(), 2)


if __name__ == "__main__":
    unittest.main()
