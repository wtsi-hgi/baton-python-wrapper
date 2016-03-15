from baton._baton_mappers import BatonDataObjectMapper, BatonCollectionMapper, BatonSpecificQueryMapper


class Connection:
    """
    TODO
    """
    def __init__(self, baton_binaries_directory: str, skip_baton_binaries_validation: bool=False):
        """
        Constructor.
        :param baton_binaries_directory: the directory host of the baton binaries
        :param skip_baton_binaries_validation: whether checks on if the correct baton binaries exist within the given
        directory should be skipped
        """
        self.data_object = BatonDataObjectMapper(baton_binaries_directory, skip_baton_binaries_validation)
        self.collection = BatonCollectionMapper(baton_binaries_directory, skip_baton_binaries_validation)
        self.specific_query = BatonSpecificQueryMapper(baton_binaries_directory, skip_baton_binaries_validation)


def connect_to_irods_with_baton(baton_binaries_directory: str) -> Connection:
    """
    TODO
    :param baton_binaries_directory:
    :param irods_query_zone:
    :return:
    """
    return Connection(baton_binaries_directory)


