import json
import unittest

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import SearchCriterion

from baton._baton_constants import BATON_COMPARISON_OPERATORS
from baton._model_to_json import model_to_baton_json, _search_criterion_to_baton_json, _search_criteria_to_baton_json, \
    _file_to_baton_json, _irods_metadata_to_baton_json
from baton.models import IrodsFile, IrodsMetadata, IrodsFileReplica

_ATTRIBUTE_1 = "attribute1"
_ATTRIBUTE_2 = "attribute2"
_VALUE_1 = "value1"
_VALUE_2 = "value2"
_VALUE_3 = "value3"
_COMPARISON_OPERATOR_1 = ComparisonOperator.EQUALS
_COMPARISON_OPERATOR_2 = ComparisonOperator.GREATER_THAN
_DIRECTORY = "collection"
_FILE_NAME = "file"
_CHECKSUM = "2c558824f250de9d55c07600291f4272"
_REPLICAS = [(1, "1c558824f250de9d55c07600291f4222"), (2, "4c558824f250de9d55c07600291f4272")]


class TestConversions(unittest.TestCase):
    def setUp(self):
        self._search_criterion1 = SearchCriterion(_ATTRIBUTE_1, _VALUE_1, _COMPARISON_OPERATOR_1)
        self._search_criterion2 = SearchCriterion(_ATTRIBUTE_2, _VALUE_2, _COMPARISON_OPERATOR_2)
        self._search_criteria = SearchCriteria([self._search_criterion1, self._search_criterion2])
        self._replicas = [IrodsFileReplica(id, checksum) for (id, checksum) in _REPLICAS]
        self._metadata = IrodsMetadata({_ATTRIBUTE_1: [_VALUE_1, _VALUE_2], _ATTRIBUTE_2: [_VALUE_3]})
        self._irods_file = IrodsFile(_DIRECTORY, _FILE_NAME, _CHECKSUM, self._replicas, self._metadata)

    def test_model_to_baton_json(self):
        self.assertIsInstance(model_to_baton_json(self._search_criterion1), dict)
        self.assertIsInstance(model_to_baton_json(self._search_criteria), dict)
        self.assertIsInstance(model_to_baton_json(self._irods_file), dict)
        self.assertIsInstance(model_to_baton_json(self._metadata), dict)

    def test__search_criterion_to_baton_json(self):
        baton_json = _search_criterion_to_baton_json(self._search_criterion1)

        self.assertIn(_ATTRIBUTE_1, baton_json.values())
        self.assertIn(_VALUE_1, baton_json.values())
        self.assertIn(BATON_COMPARISON_OPERATORS[_COMPARISON_OPERATOR_1], baton_json.values())

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
        baton_json = _irods_metadata_to_baton_json(self._metadata)
        baton_json_as_string = json.dumps(baton_json)

        for values in self._metadata:
            self.assertIn(values, baton_json_as_string)


if __name__ == "__main__":
    unittest.main()
