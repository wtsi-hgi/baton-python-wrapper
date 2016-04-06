from abc import ABCMeta, abstractmethod
from typing import Dict, List

from baton._baton._baton_runner import BatonRunner, BatonBinary
from baton._baton.json import DataObjectJSONEncoder, CollectionJSONEncoder, IrodsMetadataJSONDecoder
from baton.collections import IrodsMetadata
from baton.mappers import IrodsMetadataMapper
from baton.models import DataObject, Collection


class _BatonIrodsMetadataMapper(BatonRunner, IrodsMetadataMapper, metaclass=ABCMeta):
    """
    iRODS metadata mapper, implemented using baton.
    """
    _IRODS_METADATA_JSON_ENCODER = IrodsMetadataJSONDecoder()

    def __init__(self, additional_metadata_query_arguments: List[str], *args, **kwargs):
        """
        Constructor.
        :param additional_metadata_query_arguments: additional arguments to use in baton metadata query
        """
        super().__init__(*args, **kwargs)
        self._additional_metadata_query_arguments = additional_metadata_query_arguments

    def get_all(self, path: str) -> IrodsMetadata:
        pass

    def set(self, path: str, metadata: IrodsMetadata):
        pass

    def add(self, path: str, metadata: IrodsMetadata):
        pass

    def remove(self, path: str, metadata: IrodsMetadata):
        pass

    @abstractmethod
    def _path_to_baton_json(self, path: str) -> Dict:
        """
        Converts a path to the type of iRODS entity the mapper deals with, to its JSON representation.
        :param path: the path to convert
        :return: the JSON representation of the path
        """


class BatonDataObjectIrodsMetadataMapper(_BatonIrodsMetadataMapper):
    """
    TODO
    """
    def __init__(self, *args, **kwargs):
        super().__init__(["--obj"], *args, **kwargs)

    def _path_to_baton_json(self, path: str) -> Dict:
        data_object = DataObject(path)
        return DataObjectJSONEncoder().default(data_object)


class BatonCollectionMetadataMapper(_BatonIrodsMetadataMapper):
    """
    TODO
    """
    def __init__(self, *args, **kwargs):
        super().__init__(["--coll"], *args, **kwargs)

    def _path_to_baton_json(self, path: str) -> Dict:
        collection = Collection(path)
        return CollectionJSONEncoder().default(collection)
