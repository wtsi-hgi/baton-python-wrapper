import unittest
from abc import abstractmethod
from typing import Iterable

from baton._baton.baton_access_control_mappers import _BatonAccessControlMapper, BatonCollectionAccessControlMapper, \
    BatonDataObjectAccessControlMapper
from baton.models import Collection, IrodsEntity, AccessControl
from baton.models import DataObject
from baton.tests._baton._helpers import NAMES, create_collection, create_data_object
from baton.tests._baton._settings import BATON_DOCKER_BUILD
from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

_USERNAMES = ["user_1", "user_2", "user_3", "user_4"]


class _TestBatonAccessControlMapper(unittest.TestCase):
    """
    Tests for `_BatonAccessControlMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)
        self.mapper = self.create_mapper()

        zone = self.test_with_baton.irods_server.users[0].zone
        for username in _USERNAMES:
            self.setup_helper.create_user(username, zone)

        self.acl = [AccessControl(_USERNAMES[0], zone, AccessControl.Level.OWN),
                    AccessControl(_USERNAMES[1], zone, AccessControl.Level.WRITE),
                    AccessControl(_USERNAMES[2], zone, AccessControl.Level.READ)]
        self.access_control = AccessControl(_USERNAMES[3], zone, AccessControl.Level.OWN)

    def tearDown(self):
        self.test_with_baton.tear_down()

    @abstractmethod
    def create_mapper(self) -> _BatonAccessControlMapper:
        """
        Creates a mapper to test with.
        :return: the created mapper
        """

    @abstractmethod
    def create_irods_entity(self, name: str, acl: Iterable[AccessControl]) -> IrodsEntity:
        """
        Creates an iRODS entity to test with
        :param name: the name of the entity to create
        :param acl: the access controls the entity should have
        :return: the created entity
        """

    def test_get_all_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_all, "/invalid")

    def test_get_all(self):
        entity = self.create_irods_entity(NAMES[0], self.acl)
        self.assertEqual(self.mapper.get_all(entity.path), self.acl)

    def test_add_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.add, "/invalid", self.acl)

    def test_add_single_access_control(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add(entity.path, self.acl[0])
        self.assertCountEqual(self.mapper.get_all(entity.path), [self.access_control, self.acl[0]])

    def test_add_single_access_control_when_already_exists(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add(entity.path, self.access_control)
        self.assertEqual(self.mapper.get_all(entity.path), [self.access_control])

    def test_add_access_control_list(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add(entity.path, self.acl)
        self.assertCountEqual(self.mapper.get_all(entity.path), [self.access_control] + self.acl)

    def test_add_access_control_list_when_one_access_control_already_exists(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add(entity.path, self.acl + [self.access_control])
        self.assertEqual(self.mapper.get_all(entity.path), self.acl + [self.access_control])

    def test_set_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.set, "/invalid", self.acl)

    def test_set_when_no_existing_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], ())
        self.mapper.set(entity.path, self.acl)
        self.assertEqual(self.mapper.get_all(entity.path), self.acl)

    def test_set_when_existing_non_duplicate_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.set(entity.path, self.acl)
        self.assertEqual(self.mapper.get_all(entity.path), self.acl)

    def test_set_when_existing_duplicate_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], self.acl)
        self.mapper.set(entity.path, self.acl)
        self.assertEqual(self.mapper.get_all(entity.path), self.acl)

    def test_remove_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.remove, "/invalid", self.acl)
    #
    # def test_remove_unset_access_control(self):
    #     entity = self.create_irods_entity(NAMES[0], ())
    #     self.mapper.remove(entity.path, self.access_control)
    #
    # def test_remove_partially_unset_metadata(self):
    #     partial_metadata = deepcopy(self.metadata)
    #     del partial_metadata["key_1"]
    #     entity = self.create_irods_entity(NAMES[0], partial_metadata)
    #     self.assertRaises(KeyError, self.mapper.remove, entity.path, self.metadata)
    #
    # def test_remove(self):
    #     entity = self.create_irods_entity(NAMES[0], self.metadata)
    #     assert len(self.metadata) == 2
    #     partial_metadata_1 = deepcopy(self.metadata)
    #     del partial_metadata_1["key_1"]
    #     partial_metadata_2 = deepcopy(self.metadata)
    #     del partial_metadata_2["key_2"]
    #     self.mapper.remove(entity.path, partial_metadata_1)
    #     self.assertEqual(self.mapper.get_all(entity.path), partial_metadata_2)


class TestBatonDataObjectAccessControlMapper(_TestBatonAccessControlMapper):
    """
    Tests for `BatonDataObjectAccessControlMapper`.
    """
    def create_mapper(self) -> BatonDataObjectAccessControlMapper:
        return BatonDataObjectAccessControlMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, acl: Iterable[AccessControl]) -> DataObject:
        return create_data_object(self.test_with_baton, name, acl=acl)


class TestBatonCollectionAccessControlMapper(_TestBatonAccessControlMapper):
    """
    Tests for `BatonCollectionAccessControlMapper`.
    """
    def create_mapper(self) -> BatonCollectionAccessControlMapper:
        return BatonCollectionAccessControlMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, acl: Iterable[AccessControl]) -> Collection:
        return create_collection(self.test_with_baton, name, acl=acl)


# Trick required to stop Python's unittest from running the abstract base classes as tests
del _TestBatonAccessControlMapper


if __name__ == "__main__":
    unittest.main()
