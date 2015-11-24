import json
import unittest

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import SearchCriterion, File, Metadata

from baton._json_converters import _search_criterion_to_baton_json, _BATON_COMPARISON_OPERATORS, \
    _search_criteria_to_baton_json, _file_to_baton_json, object_to_baton_json, _baton_json_to_search_criterion, \
    _baton_json_to_irods_file, _baton_json_to_search_criteria, baton_json_to_object, _metadata_to_baton_json, \
    _baton_json_to_metadata
from baton.models import IrodsFile

_ATTRIBUTE_1 = "attribute1"
_ATTRIBUTE_2 = "attribute2"
_VALUE_1 = "value1"
_VALUE_2 = "value2"
_COMPARISON_OPERATOR_1 = ComparisonOperator.EQUALS
_COMPARISON_OPERATOR_2 = ComparisonOperator.GREATER_THAN
_DIRECTORY = "collection"
_FILE_NAME = "file"
_CHECKSUM = "2c558824f250de9d55c07600291f4272"
_REPLICA_CHECKSUMS = ["1c558824f250de9d55c07600291f4222", "4c558824f250de9d55c07600291f4272"]


class TestConversions(unittest.TestCase):
    def setUp(self):
        self._search_criterion1 = SearchCriterion(_ATTRIBUTE_1, _VALUE_1, _COMPARISON_OPERATOR_1)
        self._search_criterion2 = SearchCriterion(_ATTRIBUTE_2, _VALUE_2, _COMPARISON_OPERATOR_2)
        self._search_criteria = SearchCriteria([self._search_criterion1, self._search_criterion2])
        self._irods_file = IrodsFile(_DIRECTORY, _FILE_NAME, _CHECKSUM, _REPLICA_CHECKSUMS)
        self._metadata = Metadata(_ATTRIBUTE_1, _VALUE_1)

    def test_object_to_baton_json(self):
        self.assertIsInstance(object_to_baton_json(self._search_criterion1), dict)
        self.assertIsInstance(object_to_baton_json(self._search_criteria), dict)
        self.assertIsInstance(object_to_baton_json(self._irods_file), dict)
        self.assertIsInstance(object_to_baton_json(self._metadata), dict)

    def test__search_criterion_to_baton_json(self):
        baton_json = _search_criterion_to_baton_json(self._search_criterion1)

        self.assertIn(_ATTRIBUTE_1, baton_json.values())
        self.assertIn(_VALUE_1, baton_json.values())
        self.assertIn(_BATON_COMPARISON_OPERATORS[_COMPARISON_OPERATOR_1], baton_json.values())

    def test__search_criteria_to_baton_json(self):
        baton_json = _search_criteria_to_baton_json(self._search_criteria)

        expect_in_json = [_ATTRIBUTE_1, _VALUE_1, _ATTRIBUTE_2, _VALUE_2]
        for expected in expect_in_json:
            self.assertIn(expected, json.dumps(baton_json))

    def test__file_to_baton_json(self):
        baton_json = _file_to_baton_json(self._irods_file)

        self.assertIn(_DIRECTORY, baton_json.values())
        self.assertIn(_FILE_NAME, baton_json.values())

    def test__metadata_to_baton_json(self):
        baton_json = _metadata_to_baton_json(self._metadata)

        self.assertIn(_ATTRIBUTE_1, baton_json.values())
        self.assertIn(_VALUE_1, baton_json.values())

    def test_baton_json_to_object(self):
        self.assertIsInstance(baton_json_to_object(object_to_baton_json(self._search_criterion1), SearchCriterion), SearchCriterion)
        self.assertIsInstance(baton_json_to_object(object_to_baton_json(self._search_criteria), SearchCriteria), SearchCriteria)
        self.assertIsInstance(baton_json_to_object(object_to_baton_json(self._metadata), Metadata), Metadata)

    def test__baton_json_to_search_criterion(self):
        baton_json = object_to_baton_json(self._search_criterion1)
        self.assertEquals(_baton_json_to_search_criterion(baton_json), self._search_criterion1)

    def test__baton_json_to_search_criteria(self):
        baton_json = object_to_baton_json(self._search_criteria)
        self.assertEquals(_baton_json_to_search_criteria(baton_json), self._search_criteria)

    def test__baton_json_to_metadata(self):
        baton_json = object_to_baton_json(self._metadata)
        self.assertEquals(_baton_json_to_metadata(baton_json), self._metadata)

if __name__ == '__main__':
    unittest.main()
