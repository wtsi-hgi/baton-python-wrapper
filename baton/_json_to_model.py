from typing import Iterable, Optional

from baton._constants import BATON_ATTRIBUTE_PROPERTY, BATON_COLLECTION_PROPERTY, BATON_DATA_OBJECT_PROPERTY,\
    BATON_CHECKSUM_PROPERTY, BATON_METADATA_PROPERTY, BATON_REPLICA_PROPERTY, BATON_REPLICA_NUMBER_PROPERTY, \
    BATON_ACL_LEVEL_PROPERTY, BATON_ACL_OWNER_PROPERTY, BATON_ACL_ZONE_PROPERTY, BATON_ACL_PROPERTY, BATON_ACL_LEVELS, \
    BATON_LOCATION_PROPERTY, BATON_RESOURCE_PROPERTY
from baton._constants import BATON_VALUE_PROPERTY
from baton.models import IrodsMetadata, DataObjectReplica, AccessControl, DataObject, Collection, PreparedSpecificQuery


def baton_json_to_data_object(baton_json: dict) -> DataObject:
    """
    Converts a given baton JSON representation of a iRODS data object to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return DataObject(
        "%s/%s" % (baton_json[BATON_COLLECTION_PROPERTY], baton_json[BATON_DATA_OBJECT_PROPERTY]),
        _extract_acl_from_baton_json(baton_json),
        _extract_metadata_from_baton_json(baton_json),
        _extract_replicas_from_baton_json(baton_json)
    )


def baton_json_to_collection(baton_json: dict) -> Collection:
    """
    Converts a given baton JSON representation of a iRODS collection to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return Collection(
        baton_json[BATON_COLLECTION_PROPERTY],
        _extract_acl_from_baton_json(baton_json),
        _extract_metadata_from_baton_json(baton_json)
    )


def _baton_json_to_irods_data_object_replica(baton_json: dict) -> DataObjectReplica:
    """
    Converts a given baton JSON representation of a iRODS file replica to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return DataObjectReplica(
        baton_json[BATON_REPLICA_NUMBER_PROPERTY],
        baton_json[BATON_CHECKSUM_PROPERTY],
        baton_json[BATON_LOCATION_PROPERTY],
        baton_json[BATON_RESOURCE_PROPERTY]
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


def _baton_json_to_access_control(baton_json: dict) -> AccessControl:
    """
    Converts a given baton JSON representation of an access control item.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return AccessControl(
        baton_json[BATON_ACL_OWNER_PROPERTY],
        baton_json[BATON_ACL_ZONE_PROPERTY],
        {value: key for key, value in BATON_ACL_LEVELS.items()}[baton_json[BATON_ACL_LEVEL_PROPERTY]]
    )


def _extract_metadata_from_baton_json(baton_json: dict) -> Optional[IrodsMetadata]:
    """
    Extract metadata from the given baton JSON.
    :param baton_json: the baton JSON
    :return: the extracted metadata (`None` if none was found)
    """
    metadata = None
    if BATON_METADATA_PROPERTY in baton_json:
        metadata = _baton_json_to_irods_metadata(baton_json[BATON_METADATA_PROPERTY])
    return metadata


def _extract_replicas_from_baton_json(baton_json: dict) -> Iterable[DataObjectReplica]:
    """
    Extract replicas from the given baton JSON.
    :param baton_json: the baton JSON
    :return: the extracted replicas
    """
    replicas = []
    if BATON_REPLICA_PROPERTY in baton_json:
        for replica_as_json in baton_json[BATON_REPLICA_PROPERTY]:
            replica = _baton_json_to_irods_data_object_replica(replica_as_json)
            replicas.append(replica)
    return replicas


def _extract_acl_from_baton_json(baton_json: dict) -> Iterable[AccessControl]:
    """
    Extract the access control list from the given baton JSON.
    :param baton_json: the baton JSON
    :return: the extracted ACL
    """
    acl = []
    if BATON_ACL_PROPERTY in baton_json:
        for access_control_as_json in baton_json[BATON_ACL_PROPERTY]:
            access_control = _baton_json_to_access_control(access_control_as_json)
            acl.append(access_control)
    return acl
