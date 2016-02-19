from typing import Iterable

from baton.collections import IrodsMetadata
from baton.models import DataObject, DataObjectReplica, AccessControl, Collection
from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper


def create_data_object(test_with_baton: TestWithBatonSetup, name: str, metadata: IrodsMetadata()) -> DataObject:
    """
    Factory method to create an iRODS data object that has metadata, an ACL and replicas.
    :param test_with_baton: framework to allow testing with baton
    :param name: the name given to the created data object
    :param metadata: the metadata to give the file
    :return: the created iRODS file
    """
    user = test_with_baton.irods_server.users[0]
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    path = setup_helper.create_data_object(name)
    setup_helper.add_metadata_to(path, metadata)
    checksum = setup_helper.get_checksum(path)
    replicas = []
    for i in range(2):
        replica_storage = setup_helper.create_replica_storage()
        setup_helper.replicate_data_object(path, replica_storage)
        replica = DataObjectReplica(i + 1, checksum, replica_storage.host, replica_storage.name, True)
        replicas.append(replica)
    setup_helper.update_checksums(path)

    # Difficult to get all the details of replica 0 using icommands so remove
    setup_helper.run_icommand(["irm", "-n", "0", path])

    acl = [AccessControl(user.username, user.zone, AccessControl.Level.OWN)]

    return DataObject(path=path, access_control_list=acl, metadata=metadata, replicas=replicas)


def create_collection(test_with_baton: TestWithBatonSetup, name: str, metadata: IrodsMetadata()) -> Collection:
    """
    Factory method to create an iRODS collection that has metadata and an ACL.
    :param test_with_baton: framework to allow testing with baton
    :param name: the name given to the created collection
    :param metadata: the metadata to give the file
    :return: the created iRODS file
    """
    user = test_with_baton.irods_server.users[0]
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    path = setup_helper.create_collection(name)

    setup_helper.add_metadata_to(path, metadata)

    acl = [AccessControl(user.username, user.zone, AccessControl.Level.OWN)]

    return Collection(path=path, access_control_list=acl, metadata=metadata)


def combine_metadata(metadata_collection: Iterable[IrodsMetadata]) -> IrodsMetadata:
    """
    Combines n metadata objects into a single metadata object. Key values are merged, duplicate values are removed.
    :param metadata_collection: the collection of metadata to combine
    :return: the combined metadata
    """
    combined = IrodsMetadata()
    for metadata in metadata_collection:
        for key, values in metadata.items():
            for value in values:
                combined.add(key, value)
    return combined
