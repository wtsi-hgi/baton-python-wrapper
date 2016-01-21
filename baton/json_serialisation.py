from json import JSONEncoder

from hgicommon.json import DefaultSupportedReturnType
from hgicommon.json_conversion import MetadataJSONEncoder, ModelJSONEncoder

from baton import IrodsEntity, DataObject
from baton.collections import DataObjectReplicaCollection

# `IrodsMetadata` JSON encoder can be the same as the `Metadata` JSON encoder as it has no additional properties
IrodsMetadataJSONEncoder = MetadataJSONEncoder


class DataObjectReplicaCollectionJSONEncoder(JSONEncoder):
    """
    JSON encoder for `DataObjectReplicaCollection`.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data_object_replica_encoder = ModelJSONEncoder(**kwargs)

    def default(self, to_encode: DataObjectReplicaCollection) -> DefaultSupportedReturnType:
        if not isinstance(to_encode, DataObjectReplicaCollection):
            super().default(to_encode)

        replicas = []
        for replica in to_encode.get_all():
            replicas.append(self._data_object_replica_encoder.default(replica))

        return replicas


class IrodsEntityJSONEncoder(JSONEncoder):
    """
    JSON encoder for `IrodsEntity`.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._metadata_encoder = MetadataJSONEncoder(**kwargs)

    def default(self, to_encode: IrodsEntity) -> DefaultSupportedReturnType:
        if not isinstance(to_encode, IrodsEntity):
            super().default(to_encode)

        # TODO: Fix hardcoded strings used with property values
        return {
            "path": to_encode.path,
            "acl": to_encode.acl,
            "metadata": self._metadata_encoder.default(to_encode)
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
            super().default(to_encode)

        encoded = super().encode(to_encode)
        encoded.update(self._replicas_encoder.default(to_encode.replicas))
        return encoded
