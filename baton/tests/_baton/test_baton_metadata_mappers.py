import unittest
from copy import deepcopy

from baton.tests._settings import BATON_DOCKER_BUILD

from baton._baton.baton_metadata_mappers import BatonIrodsMetadataMapper
from baton.collections import IrodsMetadata
from baton.tests._baton._helpers import create_data_object, NAMES
from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper


class TestBatonIrodsEntityMetadataMapper(unittest.TestCase):
    """
    Tests for `BatonIrodsMetadataMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup(baton_docker_build=BATON_DOCKER_BUILD)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)
        self.mapper = BatonIrodsMetadataMapper(self.test_with_baton.baton_location)
        self.metadata = IrodsMetadata({"key_1": {"value_1", "value_2"}, "key_2": {"value_3"}})

    def test_get_all_when_invalid_path(self):
        self.assertRaises(ValueError, self.mapper.get_all, "/invalid")

    def test_get_all(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_add_when_invalid_path(self):
        self.assertRaises(ValueError, self.mapper.add, "/invalid", self.metadata)

    def test_add(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], IrodsMetadata())
        self.mapper.add(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_add_metadata_with_same_key(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], self.metadata)
        del self.metadata["key_1"]
        self.assertRaises(ValueError, self.mapper.add, entity.path, self.metadata)

    def test_set_when_invalid_path(self):
        self.assertRaises(ValueError, self.mapper.set, "/invalid", self.metadata)

    def test_set_when_no_existing_metadata(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], IrodsMetadata())
        self.mapper.set(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_set_when_existing_non_duplicate_metadata(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], IrodsMetadata({"another": {"value"}}))
        self.mapper.set(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_set_when_existing_duplicate_metadata(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], self.metadata)
        self.mapper.set(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_remove_when_invalid_path(self):
        self.assertRaises(ValueError, self.mapper.remove, "/invalid", self.metadata)

    def test_remove_unset_metadata(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], IrodsMetadata())
        self.assertRaises(KeyError, self.mapper.remove, entity.path, self.metadata)

    def test_remove_partially_unset_metadata(self):
        partial_metadata = deepcopy(self.metadata)
        del partial_metadata["key_1"]
        entity = create_data_object(self.test_with_baton, NAMES[0], partial_metadata)
        self.assertRaises(KeyError, self.mapper.remove, entity.path, self.metadata)

    def test_remove(self):
        entity = create_data_object(self.test_with_baton, NAMES[0], self.metadata)
        assert len(self.metadata) == 2
        partial_metadata_1 = deepcopy(self.metadata)
        del partial_metadata_1["key_1"]
        partial_metadata_2 = deepcopy(self.metadata)
        del partial_metadata_2["key_2"]
        self.mapper.remove(entity.path, partial_metadata_1)
        self.assertEqual(self.mapper.get_all(entity.path), partial_metadata_2)


if __name__ == "__main__":
    unittest.main()
