import json
import unittest

from baton.models import DataObjectReplica

from baton.collections import DataObjectReplicaCollection

from baton.json_serialisation import DataObjectReplicaCollectionJSONEncoder


# class TestDataObjectReplicaCollectionJSONEncoder(unittest.TestCase):
#     """
#     Tests for `DataObjectReplicaCollectionJSONEncoder`.
#     """
#     def setUp(self):
#         self._encoder = DataObjectReplicaCollectionJSONEncoder()
#         self._replicas = [DataObjectReplica(i, str(i), str(i), str(i), True) for i in range(10)]
#         self._encodable = DataObjectReplicaCollection(self._replicas)
#
#     def test_decode(self):
#         json.dumps(self._encodable, cls=self._encoder)
#
