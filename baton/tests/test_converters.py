import json
import unittest

from baton.enums import ComparisonOperator
from baton.json_converters import _search_criterion_to_baton_json, _BATON_COMPARISON_OPERATORS, \
    _search_criteria_to_baton_json, _irods_file_to_baton_json, object_to_baton_json
from baton.models import SearchCriterion, SearchCriteria, IrodsFile


_SEARCH_ATTRIBUTE_1 = "attribute1"
_SEARCH_ATTRIBUTE_2 = "attribute2"
_SEARCH_VALUE_1 = "value1"
_SEARCH_VALUE_2 = "value2"
_SEARCH_COMPARISON_OPERATOR_1 = ComparisonOperator.EQUALS
_SEARCH_COMPARISON_OPERATOR_2 = ComparisonOperator.GREATER_THAN
_DIRECTORY = "collection"
_FILE_NAME = "file"


class TestConversions(unittest.TestCase):
    def setUp(self):
        self._search_criterion1 = SearchCriterion(_SEARCH_ATTRIBUTE_1, _SEARCH_VALUE_1, _SEARCH_COMPARISON_OPERATOR_1)
        self._search_criterion2 = SearchCriterion(_SEARCH_ATTRIBUTE_2, _SEARCH_VALUE_2, _SEARCH_COMPARISON_OPERATOR_2)
        self._search_criteria = SearchCriteria([self._search_criterion1, self._search_criterion2])
        self._irods_file_location = IrodsFile(_DIRECTORY, _FILE_NAME)

    def test_object_to_baton_json(self):
        self.assertIsInstance(object_to_baton_json(self._search_criterion1), dict)
        self.assertIsInstance(object_to_baton_json(self._search_criteria), dict)
        self.assertIsInstance(object_to_baton_json(self._irods_file_location), dict)

    def test__search_criterion_to_baton_json(self):
        baton_json = _search_criterion_to_baton_json(self._search_criterion1)

        self.assertIn(_SEARCH_ATTRIBUTE_1, baton_json.values())
        self.assertIn(_SEARCH_VALUE_1, baton_json.values())
        self.assertIn(_BATON_COMPARISON_OPERATORS[_SEARCH_COMPARISON_OPERATOR_1], baton_json.values())

    def test__search_criteria_to_baton_json(self):
        baton_json = _search_criteria_to_baton_json(self._search_criteria)

        expect_in_json = [_SEARCH_ATTRIBUTE_1, _SEARCH_VALUE_1, _SEARCH_ATTRIBUTE_2, _SEARCH_VALUE_2]
        for expected in expect_in_json:
            self.assertIn(expected, json.dumps(baton_json))

    def test__irods_file_location_to_baton_json(self):
        baton_json = _irods_file_to_baton_json(self._irods_file_location)

        self.assertIn(_DIRECTORY, baton_json.values())
        self.assertIn(_FILE_NAME, baton_json.values())

if __name__ == '__main__':
    unittest.main()
