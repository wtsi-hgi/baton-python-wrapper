import json
import unittest

from hgicommon.collections import SearchCriteria
from hgicommon.enums import ComparisonOperator
from hgicommon.models import SearchCriterion

from baton._json_to_model import baton_json_to_model, _baton_json_to_search_criterion, _baton_json_to_search_criteria, \
    _baton_json_to_irods_metadata, _baton_json_to_irods_file_replica, _baton_json_to_irods_file
from baton._model_to_json import model_to_baton_json
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

    def test_baton_json_to_object(self):
        self.assertEquals(baton_json_to_model(model_to_baton_json(self._search_criterion1), SearchCriterion), self._search_criterion1)
        self.assertEquals(baton_json_to_model(model_to_baton_json(self._search_criteria), SearchCriteria), self._search_criteria)
        self.assertEquals(baton_json_to_model(model_to_baton_json(self._metadata), IrodsMetadata), self._metadata)

    def test__baton_json_to_search_criterion(self):
        baton_json = model_to_baton_json(self._search_criterion1)
        self.assertEquals(_baton_json_to_search_criterion(baton_json), self._search_criterion1)

    def test__baton_json_to_search_criteria(self):
        baton_json = model_to_baton_json(self._search_criteria)
        self.assertEquals(_baton_json_to_search_criteria(baton_json), self._search_criteria)

    def test__baton_json_to_metadata(self):
        baton_json = model_to_baton_json(self._metadata)
        self.assertEquals(_baton_json_to_irods_metadata(baton_json), self._metadata)


if __name__ == "__main__":
    unittest.main()
