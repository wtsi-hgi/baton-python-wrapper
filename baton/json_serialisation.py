from hgicommon.json_conversion import MetadataJSONEncoder

# `IrodsMetadata` JSON encoder can be the same as the `Metadata` JSON encoder as it has no additional properties
IrodsMetadataJSONEncoder = MetadataJSONEncoder