from abc import ABCMeta, abstractmethod
from typing import List, Generic, TypeVar
from typing import Union

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion

from baton.models import EntityType, Collection, DataObject, SpecificQuery


# XXX: For some reason, generics and abstract don't get along...
class IrodsEntityMapper(Generic[EntityType], metaclass=ABCMeta):
    """
    iRODS entity mapper.
    """
    @abstractmethod
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria],
                        load_metadata: bool=True) -> List[EntityType]:
        """
        Gets files from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :param load_metadata: whether the file's associated metadata should also be loaded
        :return: the matched files in iRODS
        """
        pass

    @abstractmethod
    def get_by_path(self, paths: Union[str, List[str]], load_metadata: bool=True) -> List[EntityType]:
        """
        Gets information about the given paths from iRODS.

        If one or more of the paths does not exist, a `FileNotFound` exception will be raised.
        :param paths: the paths to get from iRODS
        :param load_metadata: whether metadata associated to the paths should be loaded
        :return: the file information loaded from iRODS
        """
        pass


class DataObjectMapper(IrodsEntityMapper[DataObject], metaclass=ABCMeta):
    """
    iRODS data object mapper.
    """
    @abstractmethod
    def get_all_in_collection(self, collection_paths: Union[str, List[str]], load_metadata: bool=True) \
            -> List[DataObject]:
        """
        Gets information about files in the given iRODS collection_paths.

        If one or more of the collection_paths does not exist, a `FileNotFound` exception will be raised.
        :param collection_paths: the collection_paths to get the files from
        :param load_metadata: whether metadata associated to the files should be loaded
        :return: the file information loaded from iRODS
        """
        pass


class CollectionMapper(IrodsEntityMapper[Collection], metaclass=ABCMeta):
    """
    iRODS collection mapper.
    """
    pass


# Object type returned by the custom object mapper
_CustomObjectType = TypeVar('T')


class CustomObjectMapper(Generic[_CustomObjectType]):
    """
    Mapper for a custom object, retrieved from iRODS using a pre-installed specific query.
    """
    @abstractmethod
    def get_using_specific_query(self, specific_query: SpecificQuery) -> List[_CustomObjectType]:
        """
        Gets an object from iRODS using a specific query.
        :param specific_query: the specific query to use
        :return: Python model of the object returned from iRODS using the specific query
        """
        pass
