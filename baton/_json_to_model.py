from hgicommon.collections import Metadata

from baton._baton_constants import BATON_ATTRIBUTE_PROPERTY, BATON_DIRECTORY_PROPERTY, BATON_FILE_NAME_PROPERTY, BATON_FILE_CHECKSUM_PROPERTY, \
    BATON_METADATA_PROPERTY, BATON_FILE_REPLICATE_PROPERTY, BATON_FILE_REPLICATE_ID_PROPERTY, \
    BATON_ACL_LEVEL_PROPERTY, BATON_ACL_OWNER_PROPERTY, BATON_ACL_ZONE_PROPERTY, BATON_ACL_PROPERTY, BATON_ACL_LEVELS
from baton._baton_constants import BATON_VALUE_PROPERTY
from baton.models import IrodsFile, IrodsMetadata, IrodsFileReplica, IrodsAccessControl


def baton_json_to_irods_file(baton_json: dict) -> IrodsFile:
    """
    Converts a given baton JSON representation of a iRODS file to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    replicas = []
    if BATON_FILE_REPLICATE_PROPERTY in baton_json:
        for replica_as_json in baton_json[BATON_FILE_REPLICATE_PROPERTY]:
            replica = _baton_json_to_irods_file_replica(replica_as_json)
            replicas.append(replica)

    metadata = None
    if BATON_METADATA_PROPERTY in baton_json:
        metadata = _baton_json_to_irods_metadata(baton_json[BATON_METADATA_PROPERTY])

    acls = []
    if BATON_ACL_PROPERTY in baton_json:
        for access_control_as_json in baton_json[BATON_ACL_PROPERTY]:
            acl = _baton_json_to_irods_access_control(access_control_as_json)
            acls.append(acl)

    return IrodsFile(
        baton_json[BATON_DIRECTORY_PROPERTY],
        baton_json[BATON_FILE_NAME_PROPERTY],
        baton_json[BATON_FILE_CHECKSUM_PROPERTY],
        acls,
        replicas,
        metadata
    )


def _baton_json_to_irods_file_replica(baton_json: dict) -> IrodsFileReplica:
    """
    Converts a given baton JSON representation of a iRODS file replica to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return IrodsFileReplica(
        baton_json[BATON_FILE_REPLICATE_ID_PROPERTY],
        baton_json[BATON_FILE_CHECKSUM_PROPERTY]
    )


def _baton_json_to_irods_metadata(baton_json: dict) -> IrodsMetadata:
    """
    Converts a given baton JSON representation of collection of metadata to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    metadata = IrodsMetadata()
    for metadatum_as_json in baton_json:
        key = metadatum_as_json[BATON_ATTRIBUTE_PROPERTY]
        value = metadatum_as_json[BATON_VALUE_PROPERTY]

        if key not in metadata:
            metadata[key] = {value}
        else:
            assert isinstance(metadata[key], set)
            if value in metadata[key]:
                raise ValueError("Duplicate values are not allowed in iRODS metadata")
            metadata[key].add(value)
    return metadata


def _baton_json_to_irods_access_control(baton_json: dict) -> IrodsAccessControl:
    """
    Converts a given baton JSON representation of an access control item.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return IrodsAccessControl(
        baton_json[BATON_ACL_OWNER_PROPERTY],
        baton_json[BATON_ACL_ZONE_PROPERTY],
        {value: key for key, value in BATON_ACL_LEVELS.items()}[baton_json[BATON_ACL_LEVEL_PROPERTY]]
    )
