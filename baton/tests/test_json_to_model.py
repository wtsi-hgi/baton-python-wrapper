import unittest

from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

from baton._baton_mappers import BatonBinary
from baton._json_to_model import baton_json_to_irods_file
from baton._model_to_json import file_to_baton_json
from baton.models import IrodsFile, IrodsMetadata, IrodsFileReplica, IrodsAccessControl
from baton.tests._helpers import create_irods_file
from baton.tests._stubs import StubBatonIrodsMapper

_ATTRIBUTE_1 = "attribute1"
_ATTRIBUTE_2 = "attribute2"
_VALUE_1 = "value1"
_VALUE_2 = "value2"
_VALUE_3 = "value3"
_FILE_NAME = "file"


class TestConversions(unittest.TestCase):
    def setUp(self):
        self.test_with_baton = TestWithBatonSetup()
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)
        self.baton_irods_mapper = StubBatonIrodsMapper(
            self.test_with_baton.baton_location, self.test_with_baton.irods_test_server.users[0].zone)

        metadata = IrodsMetadata({_ATTRIBUTE_1: {_VALUE_1, _VALUE_2}, _ATTRIBUTE_2: {_VALUE_3}})
        self.irods_file = create_irods_file(self.test_with_baton, _FILE_NAME, metadata)

    def test_baton_json_to_irods_file(self):
        arguments = ["--obj", "--checksum", "--replicate", "--avu", "--acl"]
        baton_out_as_json = self.baton_irods_mapper.run_baton_query(
            BatonBinary.BATON_LIST, arguments, input_data=file_to_baton_json(self.irods_file.cast_to_file()))

        self.assertEquals(len(baton_out_as_json), 1)
        self.assertEquals(baton_json_to_irods_file(baton_out_as_json[0]), self.irods_file)

    def tearDown(self):
        self.test_with_baton.tear_down()


if __name__ == "__main__":
    unittest.main()
