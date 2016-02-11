from abc import ABCMeta, abstractmethod
from typing import Generic, Union, Sequence, Iterable

from hgicommon.models import SearchCriterion

from baton.models import Collection, DataObject, PreparedSpecificQuery, SpecificQuery
from baton.types import EntityType, CustomObjectType


class IrodsEntityMapper(Generic[EntityType], metaclass=ABCMeta):
    """
    iRODS entity mapper.
    """
    @abstractmethod
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, Iterable[SearchCriterion]],
                        load_metadata: bool=True) -> Sequence[EntityType]:
        """
        Gets files from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :param load_metadata: whether the file's associated metadata should also be loaded
        :return: the matched files in iRODS
        """
        pass

    @abstractmethod
    def get_by_path(self, paths: Union[str, Sequence[str]], load_metadata: bool=True) -> Sequence[EntityType]:
        """
        Gets entities in the given paths from iRODS.

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
    def get_all_in_collection(self, collection_paths: Union[str, Sequence[str]], load_metadata: bool=True) \
            -> Sequence[DataObject]:
        """
        Gets data objects in the given iRODS collections.

        If one or more of the collection_paths does not exist, a `FileNotFound` exception will be raised.
        :param collection_paths: the collection(s) to get the files from
        :param load_metadata: whether metadata associated to the files should be loaded
        :return: the file information loaded from iRODS
        """
        pass


class CollectionMapper(IrodsEntityMapper[Collection], metaclass=ABCMeta):
    """
    iRODS collection mapper.
    """
    pass


class CustomObjectMapper(Generic[CustomObjectType], metaclass=ABCMeta):
    """
    Mapper for a custom object, retrieved from iRODS using a pre-installed specific query.
    """
    @abstractmethod
    def _get_with_prepared_specific_query(self, specific_query: PreparedSpecificQuery) -> Sequence[CustomObjectType]:
        """
        Gets an object from iRODS using a specific query.
        :param specific_query: the specific query to use
        :return: Python model of the object returned from iRODS using the specific query
        """
        pass


class SpecificQueryMapper(CustomObjectMapper[SpecificQuery], metaclass=ABCMeta):
    """
    Mapper for specific queries installed on iRODS, implemented using baton.
    """
    @abstractmethod
    def get_all(self) -> Sequence[SpecificQuery]:
        """
        Gets all of the specific queries installed on the iRODS server.
        :return: all of the installed queries
        """
        pass
