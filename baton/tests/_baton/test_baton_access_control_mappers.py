import unittest
from abc import abstractmethod
from typing import Iterable

from baton._baton.baton_access_control_mappers import _BatonAccessControlMapper, BatonDataObjectAccessControlMapper, \
    BatonCollectionAccessControlMapper
from baton.models import DataObject, Collection
from baton.models import IrodsEntity, AccessControl
from baton.tests._baton._helpers import NAMES, create_data_object, create_collection
from baton.tests._baton._settings import BATON_DOCKER_BUILD
from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

_USERNAMES = ["user_1", "user_2", "user_3"]


class _TestBatonAccessControlMapper(unittest.TestCase):
    """
    Tests for `_BatonAccessControlMapper`.
    """
    @abstractmethod
    def create_mapper(self) -> _BatonAccessControlMapper:
        """
        Creates a mapper to test with.
        :return: the created mapper
        """

    @abstractmethod
    def create_irods_entity(self, name: str, access_controls: Iterable[AccessControl]) -> IrodsEntity:
        """
        Creates an iRODS entity to test with
        :param name: the name of the entity to create
        :param access_controls: the access controls the entity should have
        :return: the created entity
        """

    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)
        self.mapper = self.create_mapper()

        for username in _USERNAMES:
            self.setup_helper.create_user(username, self.test_with_baton.irods_server.users[0].zone)

        self.access_controls = [AccessControl(_USERNAMES[0], AccessControl.Level.WRITE),
                                AccessControl(_USERNAMES[1], AccessControl.Level.READ)]
        self.access_control = AccessControl(_USERNAMES[2], AccessControl.Level.OWN)

    def tearDown(self):
        self.test_with_baton.tear_down()

    def test_get_all_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_all, "/invalid")

    def test_get_all(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_add_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.add_or_replace, "/invalid", self.access_controls)

    def test_add_single_access_control(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_controls[0])
        self.assertCountEqual(self.mapper.get_all(entity.path), [self.access_control, self.access_controls[0]])

    def test_add_single_access_control_when_already_exists(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_control)
        self.assertEqual(self.mapper.get_all(entity.path), {self.access_control})

    def test_add_access_control_list(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_controls)
        self.assertCountEqual(self.mapper.get_all(entity.path), [self.access_control] + self.access_controls)

    def test_add_access_control_list_when_one_access_control_already_exists(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.add_or_replace(entity.path, self.access_controls + [self.access_control])
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls + [self.access_control]))

    def test_set_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.set, "/invalid", self.access_controls)

    def test_set_when_no_existing_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], ())
        self.mapper.set(entity.path, self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_set_when_existing_non_duplicate_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], [self.access_control])
        self.mapper.set(entity.path, self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_set_when_existing_duplicate_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls)
        self.mapper.set(entity.path, self.access_controls)
        self.assertEqual(self.mapper.get_all(entity.path), set(self.access_controls))

    def test_remove_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.revoke, "/invalid", self.access_controls)

    def test_remove_unset_access_control(self):
        entity = self.create_irods_entity(NAMES[0], ())
        self.mapper.revoke(entity.path, self.access_control)
        self.assertEqual(self.mapper.get_all(entity.path), set())

    def test_remove_subset_of_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls + [self.access_control])
        print(self.mapper.get_all(entity.path))
        self.mapper.revoke(entity.path, self.access_controls)
        print(self.mapper.get_all(entity.path))
        print({self.access_control})
        self.assertEqual(self.mapper.get_all(entity.path), {self.access_control})

    def test_remove_all_with_invalid_path(self):
        self.assertRaises(FileNotFoundError, self.mapper.revoke_all, "/invalid")

    def test_remove_all_with_no_access_controls(self):
        entity = self.create_irods_entity(NAMES[0], ())
        self.mapper.revoke_all(entity.path)
        self.assertEqual(self.mapper.get_all(entity.path), set())

    def test_remove_all(self):
        entity = self.create_irods_entity(NAMES[0], self.access_controls)
        self.mapper.revoke_all(entity.path)
        self.assertEqual(self.mapper.get_all(entity.path), set())


class TestBatonDataObjectAccessControlMapper(_TestBatonAccessControlMapper):
    """
    Tests for `BatonDataObjectAccessControlMapper`.
    """
    def create_mapper(self) -> BatonDataObjectAccessControlMapper:
        return BatonDataObjectAccessControlMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, access_controls: Iterable[AccessControl]) -> DataObject:
        return create_data_object(self.test_with_baton, name, access_controls=access_controls)


class TestBatonCollectionAccessControlMapper(_TestBatonAccessControlMapper):
    """
    Tests for `BatonCollectionAccessControlMapper`.
    """
    def create_mapper(self) -> BatonCollectionAccessControlMapper:
        return BatonCollectionAccessControlMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, access_controls: Iterable[AccessControl]) -> Collection:
        return create_collection(self.test_with_baton, name, access_controls=access_controls)


# Trick required to stop Python's unittest from running the abstract base classes as tests
del _TestBatonAccessControlMapper


if __name__ == "__main__":
    unittest.main()
