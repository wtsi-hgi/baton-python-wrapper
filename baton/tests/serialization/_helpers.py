import copy
from typing import Tuple, Dict

from testwithbaton.api import TestWithBatonSetup

from baton import DataObject
from baton.baton_runner import BatonBinary
from baton.baton_runner import BatonRunner
from baton.collections import IrodsMetadata
from baton.tests._helpers import create_data_object

_data_object = None
_data_object_as_json = None


def create_data_object_with_baton_json_representation() -> Tuple[DataObject, Dict]:
    """
    Creates a data object and returns it along with the JSON representation of it given by baton.

    Uses baton to get the JSON representation on the first use: the JSON is retrieved from a cache in subsequent uses.
    :return: a tuple where the first element is the created data object and the second is it's JSON representation
    according to baton
    """
    global _data_object, _data_object_as_json

    # Starting baton is expensive - get view of baton JSON and cache
    if _data_object is None:
        test_with_baton = TestWithBatonSetup()
        test_with_baton.setup()

        metadata = IrodsMetadata({"attribute_a": {"value_1", "value_2"}, "attribute_b": {"value_3"}})
        _data_object = create_data_object(test_with_baton, "data_object_name", metadata)

        baton_query = {
            "collection": _data_object.get_collection_path(),
            "data_object": _data_object.get_name()
        }
        baton_runner = BatonRunner(
                test_with_baton.baton_location, test_with_baton.irods_test_server.users[0].zone, True)

        _data_object_as_json = baton_runner.run_baton_query(
                BatonBinary.BATON_LIST, ["--acl", "--avu", "--replicate"], input_data=baton_query)[0]

    return copy.deepcopy(_data_object), copy.deepcopy(_data_object_as_json)
