from typing import Iterable

from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

from baton.models import DataObjectReplica, AccessControl, IrodsMetadata, DataObjectPath, DataObject, CollectionPath,\
    Collection


def create_data_object(test_with_baton: TestWithBatonSetup, name: str, metadata: IrodsMetadata()) -> DataObject:
    """
    Factory method to create an iRODS data object that has metadata, an ACL and replicas.
    :param test_with_baton: framework to allow testing with baton
    :param name: the name given to the created data object
    :param metadata: the metadata to give the file
    :return: the created iRODS file
    """
    user = test_with_baton.irods_test_server.users[0]
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    location = setup_helper.create_data_object(name)
    path = DataObjectPath(location)

    setup_helper.run_icommand("icd", [path.get_collection_path()])
    setup_helper.run_icommand("irepl", [path.get_name()])
    setup_helper.add_metadata_to(path.location, metadata)
    checksum = setup_helper.get_checksum(location)

    replicas = [DataObjectReplica(0, checksum)]
    acl = [AccessControl(user.username, user.zone, AccessControl.Level.OWN)]

    return DataObject(path, checksum, acl, metadata, replicas)


def create_collection(test_with_baton: TestWithBatonSetup, name: str, metadata: IrodsMetadata()) -> DataObject:
    """
    Factory method to create an iRODS collection that has metadata and an ACL.
    :param test_with_baton: framework to allow testing with baton
    :param name: the name given to the created collection
    :param metadata: the metadata to give the file
    :return: the created iRODS file
    """
    user = test_with_baton.irods_test_server.users[0]
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    location = setup_helper.create_collection(name)
    path = CollectionPath(location)

    setup_helper.add_metadata_to(location, metadata)

    acl = [AccessControl(user.username, user.zone, AccessControl.Level.OWN)]

    return Collection(path, acl, metadata)


def combine_metadata(metadata_collection: Iterable[IrodsMetadata]) -> IrodsMetadata:
    """
    Combines n metadata objects into a single metadata object. Key values are merged, duplicate values are removed.
    :param metadata_collection: the collection of metadata to combine
    :return: the combined metadata
    """
    combined = IrodsMetadata()
    for metadata in metadata_collection:
        for key, value in metadata.items():
            if key not in combined:
                combined[key] = value
            else:
                combined[key].add(value)
    return combined
