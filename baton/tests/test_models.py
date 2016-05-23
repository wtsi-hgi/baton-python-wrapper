import copy
import unittest

from baton.models import DataObject, SpecificQuery, Collection, IrodsEntity, AccessControl, User
from baton.tests._stubs import StubIrodsEntity

_COLLECTION = "/collection/sub_collection"
_FILE_NAME = "file_name"
_CHECKSUMS = ["2c558824f250de9d55c07600291f4272", "2c558824f250de9d55c07600291f4233", "2c558824f250de9d55c07600291f4257"]
_NAME = "user_1"
_ZONE = "zone_1"


class TestIrodsEntity(unittest.TestCase):
    """
    Tests for `IrodsEntity`.
    """
    def setUp(self):
        self.path = "/test/path"
        self.access_controls = set([AccessControl(User("user_%s" % i, _ZONE), AccessControl.Level.READ)
                                    for i in range(10)])
        self.irods_entity = StubIrodsEntity(self.path, self.access_controls)

    def test_get_acl(self):
        self.assertEqual(self.irods_entity.acl, self.access_controls)

    def test_set_acl(self):
        self.irods_entity.acl = set()
        self.assertEqual(self.irods_entity.acl, set())

    def test_get_access_controls(self):
        self.assertEqual(self.irods_entity.access_controls, self.access_controls)

    def test_set_access_controls(self):
        self.irods_entity.access_controls = set()
        self.assertEqual(self.irods_entity.access_controls, set())

    def test_set_access_controls_converts_to_set(self):
        self.irods_entity.access_controls = []
        self.assertEqual(self.irods_entity.access_controls, set())


class TestDataObject(unittest.TestCase):
    """
    Tests for `DataObject`.
    """
    def setUp(self):
        self.entity = DataObject("%s/%s" % (_COLLECTION, _FILE_NAME))

    def test_cannot_create_entity_with_relative_path(self):
        self.assertRaises(ValueError, type(self.entity), "../data_object")

    def test_get_collection_path(self):
        self.assertEquals(self.entity.get_collection_path(), _COLLECTION)

    def test_get_name(self):
        self.assertEquals(self.entity.get_name(), _FILE_NAME)

    def test_equality(self):
        data_object_2 = copy.deepcopy(self.entity)
        self.assertEqual(data_object_2, self.entity)


class TestCollection(unittest.TestCase):
    """
    Tests for `Collection`.
    """
    def setUp(self):
        self.entity = Collection(_COLLECTION)

    def test_cannot_create_entity_with_relative_path(self):
        self.assertRaises(ValueError, type(self.entity), "../collection")

    def test_get_collection_path(self):
        self.assertEquals(self.entity.get_collection_path(), "/collection")

    def test_get_name(self):
        self.assertEquals(self.entity.get_name(), "sub_collection")

    def test_equality(self):
        data_object_2 = copy.deepcopy(self.entity)
        self.assertEqual(data_object_2, self.entity)

    def test_strips_trailing_slash_from_path(self):
        collection = Collection("/the/path/")
        self.assertEquals(collection.path, "/the/path")


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


class TestUser(unittest.TestCase):
    """
    Tests for `User`.
    """
    def test_create_from_str(self):
        user = User.create_from_str("%s#%s" % (_NAME, _ZONE))
        self.assertEqual(user, User(_NAME, _ZONE))

    def test_str(self):
        user = User(_NAME, _ZONE)
        self.assertEqual(str(user), "%s#%s" % (_NAME, _ZONE))


if __name__ == "__main__":
    unittest.main()
