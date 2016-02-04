import json
from json import JSONEncoder, JSONDecoder

from baton.collections import IrodsMetadata, DataObjectReplicaCollection
from baton.models import AccessControl, DataObjectReplica, DataObject, IrodsEntity
from hgijson.json.builders import MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
from hgijson.json.models import JsonPropertyMapping

# JSON encoder/decoder for `AccessControl`
from hgijson.types import PrimitiveJsonSerializableType

_ACCESS_CONTROL_LEVEL_TO_STRING_MAP = {
    AccessControl.Level.OWN: "own",
    AccessControl.Level.READ: "read",
    AccessControl.Level.WRITE: "write"
}

def access_control_level_to_string(level: AccessControl.Level):
    assert level in _ACCESS_CONTROL_LEVEL_TO_STRING_MAP
    return _ACCESS_CONTROL_LEVEL_TO_STRING_MAP[level]

def access_control_level_from_string(level_as_string: str):
    return [key for key, value in _ACCESS_CONTROL_LEVEL_TO_STRING_MAP.items() if value == level_as_string][0]

_access_control_json_mappings = [
    JsonPropertyMapping("owner", "owner", "owner"),
    JsonPropertyMapping("zone", "zone", "zone"),
    JsonPropertyMapping("level", None, "level",
                        object_property_getter=lambda access_control: access_control_level_to_string(access_control.level),
                        object_constructor_argument_modifier=lambda level_as_string: access_control_level_from_string(level_as_string))
]
AccessControlJSONEncoder = MappingJSONEncoderClassBuilder(AccessControl, _access_control_json_mappings).build()
AccessControlJSONDecoder = MappingJSONDecoderClassBuilder(AccessControl, _access_control_json_mappings).build()


# JSON encoder/decoder for `DataObjectReplica`
_data_object_replica_json_mappings = [
    JsonPropertyMapping("number", "number", "number"),
    JsonPropertyMapping("checksum", "checksum", "checksum"),
    JsonPropertyMapping("location", "host", "host"),
    JsonPropertyMapping("resource", "resource_name", "resource_name"),
    JsonPropertyMapping("valid", "up_to_date", "up_to_date")
]
DataObjectReplicaJSONEncoder = MappingJSONEncoderClassBuilder(DataObjectReplica, _data_object_replica_json_mappings).build()
DataObjectReplicaJSONDecoder = MappingJSONDecoderClassBuilder(DataObjectReplica, _data_object_replica_json_mappings).build()


# JSON encoder/decoder for `DataObjectReplicaCollection`
class DataObjectReplicaCollectionJSONEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._replica_encoder = DataObjectReplicaJSONEncoder(*args, **kwargs)   # type: JSONEncoder

    def default(self, data_object_replica_collection: DataObjectReplicaCollection) -> PrimitiveJsonSerializableType:
        if not isinstance(data_object_replica_collection, DataObjectReplicaCollection):
            return super().default(data_object_replica_collection)
        return [self._replica_encoder.default(replica) for replica in data_object_replica_collection.get_all()]

class DataObjectReplicaCollectionJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._replica_decoder = DataObjectReplicaJSONDecoder(*args, **kwargs)   # type: JSONDecoder

    def decode(self, json_as_string: str, **kwargs) -> DataObjectReplicaCollection:
        json_as_list = json.loads(json_as_string)
        if not isinstance(json_as_list, list):
            return super().decode(json_as_list)
        return DataObjectReplicaCollection([self._replica_decoder.decode(json.dumps(item)) for item in json_as_list])


# JSON encoder/decoder for `IrodsMetadata`
class IrodsMetadataJSONEncoder(JSONEncoder):
    def default(self, irods_metadata: IrodsMetadata) -> PrimitiveJsonSerializableType:
        if not isinstance(irods_metadata, IrodsMetadata):
            return super().default(irods_metadata)
        avus = []
        for key, values in irods_metadata.items():
            for value in values:
                avus.append({
                    "attribute": key,
                    "value": value
                })
        return avus

class IrodsMetadataJSONDecoder(JSONDecoder):
    def decode(self, json_as_string: str, **kwargs) -> IrodsMetadata:
        json_as_list = json.loads(json_as_string)
        if not isinstance(json_as_list, list):
            return super().decode(json_as_list)
        irods_metadata = IrodsMetadata()
        for item in json_as_list:
            assert isinstance(item, dict)
            attribute = item["attribute"]
            value = item["value"]
            if attribute in irods_metadata:
                irods_metadata[attribute].add(value)
            else:
                irods_metadata[attribute] = {value}
        return irods_metadata


# JSON encoder/decoder for `IrodsEntity`
_irods_entity_json_mappings = [
    JsonPropertyMapping(None, "path", "path",
                        json_property_getter=lambda json_as_dict: json_as_dict["collection"] + "/" + json_as_dict["data_object"]),
    JsonPropertyMapping("collection", object_property_getter=lambda irods_entity: irods_entity.get_collection_path()),
    JsonPropertyMapping("data_object", object_property_getter=lambda irods_entity: irods_entity.get_name()),
    JsonPropertyMapping("access", "acl", "access_control_list",
                        encoder_cls=AccessControlJSONEncoder, decoder_cls=AccessControlJSONDecoder),
    JsonPropertyMapping("avus", "metadata", "metadata",
                        encoder_cls=IrodsMetadataJSONEncoder, decoder_cls=IrodsMetadataJSONDecoder)
]
_IrodsEntityJSONEncoder = MappingJSONEncoderClassBuilder(IrodsEntity, _irods_entity_json_mappings).build()
_IrodsEntityJSONDecoder = MappingJSONDecoderClassBuilder(IrodsEntity, _irods_entity_json_mappings).build()


# JSON encoder/decoder for `DataObject`
_data_object_json_mappings = [
    JsonPropertyMapping("replicates", "replicas", "replicas",
                        encoder_cls=DataObjectReplicaCollectionJSONEncoder, decoder_cls=DataObjectReplicaCollectionJSONDecoder)
]
DataObjectJSONEncoder = MappingJSONEncoderClassBuilder(DataObject, _data_object_json_mappings, _IrodsEntityJSONEncoder).build()
DataObjectJSONDecoder = MappingJSONDecoderClassBuilder(DataObject, _data_object_json_mappings, _IrodsEntityJSONDecoder).build()
