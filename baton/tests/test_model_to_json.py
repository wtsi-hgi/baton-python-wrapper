import json
import unittest

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import SearchCriterion

from baton._model_to_json import search_criteria_to_baton_json, irods_metadata_to_baton_json, data_object_to_baton_json, \
    collection_to_baton_json, specific_query_to_baton_json
from baton.models import IrodsMetadata, DataObject, Collection, SpecificQuery

_ATTRIBUTE_1 = "attribute1"
_ATTRIBUTE_2 = "attribute2"
_VALUE_1 = "value1"
_VALUE_2 = "value2"
_VALUE_3 = "value3"
_COMPARISON_OPERATOR_1 = ComparisonOperator.EQUALS
_COMPARISON_OPERATOR_2 = ComparisonOperator.GREATER_THAN
_COLLECTION_LOCATION = "/collection"
_DATA_OBJECT_LOCATION = "/collection/file"
_CHECKSUM = "2c558824f250de9d55c07600291f4272"
_REPLICAS = [(1, "1c558824f250de9d55c07600291f4222"), (2, "4c558824f250de9d55c07600291f4272")]
_QUERY_ALIAS = "findQueryByAlias"
_QUERY_ARGUMENT = "lsl"


class TestConversions(unittest.TestCase):
    def setUp(self):
        self._search_criterion1 = SearchCriterion(_ATTRIBUTE_1, _VALUE_1, _COMPARISON_OPERATOR_1)
        self._search_criterion2 = SearchCriterion(_ATTRIBUTE_2, _VALUE_2, _COMPARISON_OPERATOR_2)
        self._search_criteria = SearchCriteria([self._search_criterion1, self._search_criterion2])
        self._metadata = IrodsMetadata({_ATTRIBUTE_1: {_VALUE_1, _VALUE_2}, _ATTRIBUTE_2: {_VALUE_3}})
        self._data_object = DataObject("%s/%s" % (_COLLECTION_LOCATION, _DATA_OBJECT_LOCATION))
        self._collection = Collection(_COLLECTION_LOCATION)
        self._specific_query = SpecificQuery(_QUERY_ALIAS, [_QUERY_ARGUMENT])

    def test_search_criteria_to_baton_json(self):
        baton_json = search_criteria_to_baton_json(self._search_criteria)

        self.assertIsInstance(baton_json, dict)
        expect_in_json = [_ATTRIBUTE_1, _VALUE_1, _ATTRIBUTE_2, _VALUE_2]
        for expected in expect_in_json:
            self.assertIn(expected, json.dumps(baton_json))

    def test_path_to_baton_json_with_data_object(self):
        baton_json = data_object_to_baton_json(self._data_object)

        self.assertIsInstance(baton_json, dict)
        self.assertIn(self._data_object.get_name(), baton_json.values())
        self.assertIn(self._data_object.get_directory(), baton_json.values())

    def test_path_to_baton_json_with_collection(self):
        baton_json = collection_to_baton_json(self._collection)

        self.assertIsInstance(baton_json, dict)
        self.assertIn(self._collection.path, baton_json.values())

    def test_metadata_to_baton_json(self):
        baton_json = irods_metadata_to_baton_json(self._metadata)

        self.assertIsInstance(baton_json, dict)
        baton_json_as_string = json.dumps(baton_json)
        for values in self._metadata:
            self.assertIn(values, baton_json_as_string)

    def test_specific_query_to_baton_json(self):
        baton_json = specific_query_to_baton_json(self._specific_query)

        self.assertIsInstance(baton_json, dict)
        self.assertIn(self._specific_query.query_alias, baton_json.values())
        self.assertIn(self._specific_query.query_arguments, baton_json.values())


if __name__ == "__main__":
    unittest.main()
