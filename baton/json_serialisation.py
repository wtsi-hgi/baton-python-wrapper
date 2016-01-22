from json import JSONEncoder

from hgicommon.json import DefaultSupportedReturnType
from hgicommon.json_conversion import ModelJSONEncoder

from baton import IrodsEntity, DataObject
from baton.collections import DataObjectReplicaCollection


class DataObjectReplicaCollectionJSONEncoder(JSONEncoder):
    """
    JSON encoder for `DataObjectReplicaCollection`.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data_object_replica_encoder = ModelJSONEncoder(**kwargs)

    def default(self, to_encode: DataObjectReplicaCollection) -> DefaultSupportedReturnType:
        if not isinstance(to_encode, DataObjectReplicaCollection):
            JSONEncoder.default(self, to_encode)

        replicas = []
        for replica in to_encode.get_all():
            replicas.append(self._data_object_replica_encoder.default(replica))

        return replicas


class IrodsEntityJSONEncoder(JSONEncoder):
    """
    JSON encoder for `IrodsEntity`.
    """
    def default(self, to_encode: IrodsEntity) -> DefaultSupportedReturnType:
        if not isinstance(to_encode, IrodsEntity):
            JSONEncoder.default(self, to_encode)

        return {
            "path": to_encode.path,
            "acl": to_encode.acl,
            "metadata": dict(to_encode.metadata)
        }


class DataObjectJSONEncoder(IrodsEntityJSONEncoder):
    """
    JSON encoder for `DataObject`.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._replicas_encoder = DataObjectReplicaCollectionJSONEncoder(**kwargs)

    def default(self, to_encode: DataObject) -> DefaultSupportedReturnType:
        if not isinstance(to_encode, DataObject):
            JSONEncoder.default(self, to_encode)

        encoded = super().encode(to_encode)
        encoded.update(self._replicas_encoder.default(to_encode.replicas))
        return encoded
