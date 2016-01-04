from baton._baton_mappers import BatonDataObjectMapper, BatonCollectionMapper, BatonSpecificQueryMapper


class Connection:
    """
    TODO
    """
    def __init__(self, baton_binaries_directory: str, irods_query_zone: str):
        """
        Constructor.
        :param baton_binaries_directory: the directory location of the baton binaries
        :param irods_query_zone: the iRODS query zone to work in
        """
        self.data_object = BatonDataObjectMapper(baton_binaries_directory, irods_query_zone)
        self.collection = BatonCollectionMapper(baton_binaries_directory, irods_query_zone)
        self.specific_query = BatonSpecificQueryMapper(baton_binaries_directory, irods_query_zone)


def connect_to_irods_with_baton(baton_binaries_directory: str, irods_query_zone: str) -> Connection:
    """
    TODO
    :param baton_binaries_directory:
    :param irods_query_zone:
    :return:
    """
    return Connection(baton_binaries_directory, irods_query_zone)
