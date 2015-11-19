from baton.irods_mappers import BatonMetadataMapper, BatonFileMapper, BatonMapper


class Connection:
    """
    TODO
    """
    def __init__(self, baton_binaries_directory: str, irods_query_zone: str):
        """
        TODO
        :param baton_binaries_directory:
        :param irods_query_zone:
        """
        self.metadata = BatonMetadataMapper(baton_binaries_directory, irods_query_zone)
        self.file = BatonFileMapper(baton_binaries_directory, irods_query_zone)


def connect_to_irods_with_baton(baton_binaries_directory: str, irods_query_zone: str) -> BatonMapper:
    """
    TODO
    :param baton_binaries_directory:
    :param irods_query_zone:
    :return:
    """
    return Connection(baton_binaries_directory, irods_query_zone)
