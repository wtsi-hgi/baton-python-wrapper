import unittest

from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

from baton._baton_mappers import BatonBinary
from baton._json_to_model import baton_json_to_data_object, baton_json_to_collection
from baton._model_to_json import data_object_to_baton_json, collection_to_baton_json
from baton.models import IrodsMetadata
from baton.tests._helpers import create_data_object, create_collection
from baton.tests._stubs import StubBatonRunner

_ATTRIBUTE_1 = "attribute1"
_ATTRIBUTE_2 = "attribute2"
_VALUE_1 = "value1"
_VALUE_2 = "value2"
_VALUE_3 = "value3"
_NAME = "name"


class TestConversions(unittest.TestCase):
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)

        self.baton_irods_mapper = StubBatonRunner(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)

        self.metadata = IrodsMetadata({_ATTRIBUTE_1: {_VALUE_1, _VALUE_2}, _ATTRIBUTE_2: {_VALUE_3}})

    def test_baton_json_to_data_object(self):
        data_object = create_data_object(self.test_with_baton, _NAME, self.metadata)

        arguments = ["--obj", "--replicate", "--avu", "--acl"]
        baton_out_as_json = self.baton_irods_mapper.run_baton_query(
            BatonBinary.BATON_LIST, arguments, input_data=data_object_to_baton_json(data_object))

        self.assertEquals(len(baton_out_as_json), 1)
        self.assertEquals(baton_json_to_data_object(baton_out_as_json[0]), data_object)

    def test_baton_json_to_collection(self):
        collection = create_collection(self.test_with_baton, _NAME, self.metadata)

        arguments = ["--coll", "--avu", "--acl"]
        baton_out_as_json = self.baton_irods_mapper.run_baton_query(
            BatonBinary.BATON_LIST, arguments, input_data=collection_to_baton_json(collection))

        self.assertEquals(len(baton_out_as_json), 1)
        self.assertEquals(baton_json_to_collection(baton_out_as_json[0]), collection)

    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == "__main__":
    unittest.main()
