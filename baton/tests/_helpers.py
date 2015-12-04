from testwithbaton.api import TestWithBatonSetup
from testwithbaton.helpers import SetupHelper

from baton.models import IrodsFileReplica, IrodsFile, IrodsAccessControl, IrodsMetadata


def create_irods_file(test_with_baton: TestWithBatonSetup, file_name: str, metadata: IrodsMetadata()):
    """
    Factory method to create an iRODS file that has metadata, an ACL and replicas.
    :param test_with_baton: framework to allow testing with baton
    :param metadata: the metadata to give the file
    :return: the created iRODS file
    """
    user = test_with_baton.irods_test_server.users[0]
    setup_helper = SetupHelper(test_with_baton.icommands_location)

    file = setup_helper.create_irods_file(file_name)

    setup_helper.run_icommand("icd", [file.directory])
    setup_helper.run_icommand("irepl", [file.file_name])
    setup_helper.add_metadata_to_file(file, metadata)
    checksum = setup_helper.get_checksum(file)

    replicas = [IrodsFileReplica(0, checksum)]
    acl = [IrodsAccessControl(user.username, user.zone, IrodsAccessControl.Level.OWN)]

    return IrodsFile(file.directory, file.file_name, checksum, acl, replicas, metadata)
