from baton._baton_mappers import BatonDataObjectMapper, BatonCollectionMapper, BatonSpecificQueryMapper


class Connection:
    """
    TODO
    """
    def __init__(self, baton_binaries_directory: str,):
        """
        Constructor.
        :param baton_binaries_directory: the directory host of the baton binaries
        """
        self.data_object = BatonDataObjectMapper(baton_binaries_directory)
        self.collection = BatonCollectionMapper(baton_binaries_directory)
        self.specific_query = BatonSpecificQueryMapper(baton_binaries_directory)


def connect_to_irods_with_baton(baton_binaries_directory: str) -> Connection:
    """
    TODO
    :param baton_binaries_directory:
    :param irods_query_zone:
    :return:
    """
    return Connection(baton_binaries_directory)
