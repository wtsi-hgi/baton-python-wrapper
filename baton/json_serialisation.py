from json import JSONEncoder

from baton.collections import DataObjectReplicaCollection
from hgicommon.json import DefaultSupportedReturnType
from hgicommon.json_conversion import MetadataJSONEncoder

# `IrodsMetadata` JSON encoder can be the same as the `Metadata` JSON encoder as it has no additional properties
IrodsMetadataJSONEncoder = MetadataJSONEncoder


class DataObjectReplicaCollectionJSONEncoder(JSONEncoder):
    """
    JSON encoder for `DataObjectReplicaCollection`.
    """
    def default(self, to_encode: DataObjectReplicaCollection) -> DefaultSupportedReturnType:
        if not isinstance(to_encode, DataObjectReplicaCollection):
            super().default(to_encode)

        return to_encode._data
