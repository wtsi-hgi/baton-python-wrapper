import json
import unittest

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import SearchCriterion

from baton._model_to_json import search_criteria_to_baton_json, irods_metadata_to_baton_json, data_object_to_baton_json, \
    collection_to_baton_json, prepared_specific_query_to_baton_json
from baton.models import IrodsMetadata, DataObject, Collection, PreparedSpecificQuery

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
    def test_search_criteria_to_baton_json(self):
        search_criterion1 = SearchCriterion(_ATTRIBUTE_1, _VALUE_1, _COMPARISON_OPERATOR_1)
        search_criterion2 = SearchCriterion(_ATTRIBUTE_2, _VALUE_2, _COMPARISON_OPERATOR_2)
        search_criteria = SearchCriteria([search_criterion1, search_criterion2])

        baton_json = search_criteria_to_baton_json(search_criteria)

        self.assertIsInstance(baton_json, dict)
        expect_in_json = [_ATTRIBUTE_1, _VALUE_1, _ATTRIBUTE_2, _VALUE_2]
        for expected in expect_in_json:
            self.assertIn(expected, json.dumps(baton_json))

    def test_path_to_baton_json_with_data_object(self):
        data_object = DataObject("%s/%s" % (_COLLECTION_LOCATION, _DATA_OBJECT_LOCATION))

        baton_json = data_object_to_baton_json(data_object)

        self.assertIsInstance(baton_json, dict)
        self.assertIn(data_object.get_name(), baton_json.values())
        self.assertIn(data_object.get_collection_path(), baton_json.values())

    def test_path_to_baton_json_with_collection(self):
        collection = Collection(_COLLECTION_LOCATION)

        baton_json = collection_to_baton_json(collection)

        self.assertIsInstance(baton_json, dict)
        self.assertIn(collection.path, baton_json.values())

    def test_metadata_to_baton_json(self):
        metadata = IrodsMetadata({_ATTRIBUTE_1: {_VALUE_1, _VALUE_2}, _ATTRIBUTE_2: {_VALUE_3}})

        baton_json = irods_metadata_to_baton_json(metadata)

        self.assertIsInstance(baton_json, dict)
        baton_json_as_string = json.dumps(baton_json)
        for values in metadata:
            self.assertIn(values, baton_json_as_string)

    def test_prepared_specific_query_to_baton_json(self):
        prepared_specific_query = PreparedSpecificQuery(_QUERY_ALIAS, [_QUERY_ARGUMENT])

        baton_json = prepared_specific_query_to_baton_json(prepared_specific_query)

        self.assertIsInstance(baton_json, dict)
        self.assertIn(prepared_specific_query.alias, str(baton_json.values()))
        for query_argument in prepared_specific_query.query_arguments:
            self.assertIn(query_argument, str(baton_json.values()))


if __name__ == "__main__":
    unittest.main()
