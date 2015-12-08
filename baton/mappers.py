from abc import ABCMeta, abstractmethod
from typing import List, TypeVar, Generic
from typing import Union

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion

from baton.models import CollectionPath, DataObject, Collection, DataObjectPath, EntityType, EntityPathType


class IrodsEntityMapper(Generic[EntityType, EntityPathType]):
    """
    iRODS entity mapper.
    """
    @abstractmethod
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria],
                        load_metadata: bool=False) -> List[EntityType]:
        """
        Gets files from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :param load_metadata: whether the file's associated metadata should also be loaded
        :return: the matched files in iRODS
        """
        pass

    @abstractmethod
    def get_by_path(self, paths: Union[EntityPathType, List[EntityPathType]], load_metadata: bool=True) \
            -> List[EntityType]:
        """
        Gets information about the given paths from iRODS.

        If one or more of the paths does not exist, a `FileNotFound` exception will be raised.
        :param paths: the paths to get from iRODS
        :param load_metadata: whether metadata associated to the paths should be loaded
        :return: the file information loaded from iRODS
        """
        pass


class DataObjectMapper(IrodsEntityMapper[DataObject, DataObjectPath], metaclass=ABCMeta):
    """
    TODO
    """
    @abstractmethod
    def get_all_in_collection(self, collection_paths: Union[CollectionPath, List[CollectionPath]],
                              load_metadata: bool=True) -> List[DataObject]:
        """
        Gets information about files in the given iRODS collection_paths.

        TODO: Is the below true?
        If one or more of the collection_paths does not exist, a `FileNotFound` exception will be raised.
        :param collection_paths: the collection_paths to get the files from
        :param load_metadata: whether metadata associated to the files should be loaded
        :return: the file information loaded from iRODS
        """
        pass


class CollectionMapper(IrodsEntityMapper[Collection, CollectionPath], metaclass=ABCMeta):
    """
    TODO
    """
    pass
