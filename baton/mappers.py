from abc import ABCMeta, abstractmethod, abstractproperty
from typing import Generic, Union, Sequence, Iterable

from baton.collections import IrodsMetadata

from baton.models import Collection, DataObject, PreparedSpecificQuery, SpecificQuery, SearchCriterion, IrodsEntity
from baton.types import EntityType, CustomObjectType


class IrodsMetadataMapper(Generic[EntityType], metaclass=ABCMeta):
    """
    iRODS metadata mapper.
    """
    def get_all(self, irods_entity_path: str) -> Sequence[IrodsMetadata]:
        """
        Gets all of the metadata for the given entity.
        :param irods_entity_path: the path of the entity to getr the metadata for
        :return: metadata for the given entity
        """

    def add(self, irods_entity_path: str, metadata: Union[IrodsMetadata, Iterable[IrodsMetadata]]):
        """
        Adds the given metadata or collection of metadata to the given iRODS entity.
        :param irods_entity_path: the path of the entity to add the metadata to
        :param metadata: the metadata to write
        """

    def set(self, irods_entity_path: str, metadata: Iterable[IrodsMetadata]):
        """
        Sets the given metadata or collection of metadata on the given iRODS entity.

        Similar to `add` although pre-existing metadata with matching keys will be overwritten.
        :param irods_entity_path: the path of the entity to set the metadata for
        :param metadata: the metadata to set
        """

    def remove(self, irods_entity_path: str, metadata: Iterable[IrodsMetadata]):
        """
        Removes the given metadata or collection of metadata from the given iRODS entity.

        An exception will be raised if the entity does not have metadata with the given key and value. If this exception
        is raised part-way through the removal of multiple pieces of metadata, a rollback will not occur - it would be
        necessary to get the metadata for the entity to determine what metadata in the collection was removed
        successfully.
        :param irods_entity_path: the path of the entity to remove metadata from
        :param metadata: the metadata to remove
        """


class IrodsEntityMapper(Generic[EntityType], metaclass=ABCMeta):
    """
    iRODS entity mapper.
    """
    @abstractproperty
    def metadata(self) -> IrodsMetadataMapper[EntityType]:
        """
        TODO
        :return:
        """

    @abstractmethod
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, Iterable[SearchCriterion]],
                        load_metadata: bool=True, zone: str=None) -> Sequence[EntityType]:
        """
        Gets entities from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :param load_metadata: whether metadata associated to the entities should be loaded
        :param zone: limit query to specific zone in iRODS
        :return: the matched entities in iRODS
        """

    @abstractmethod
    def get_by_path(self, paths: Union[str, Iterable[str]], load_metadata: bool=True) -> Sequence[EntityType]:
        """
        Gets entities with the given paths from iRODS.

        If one or more of the entities does not exist, a `FileNotFound` exception will be raised.
        :param paths: the paths of the entities to get from iRODS
        :param load_metadata: whether metadata associated to the entities should be loaded
        :return: the entities loaded from iRODS
        """

    @abstractmethod
    def get_all_in_collection(self, collection_paths: Union[str, Iterable[str]], load_metadata: bool = True) \
            -> Sequence[EntityType]:
        """
        Gets entities contained within the given iRODS collections.

        If one or more of the collection_paths does not exist, a `FileNotFound` exception will be raised.
        :param collection_paths: the collection(s) to get the entities from
        :param load_metadata: whether metadata associated to the entities should be loaded
        :return: the entities loaded from iRODS
        """


class DataObjectMapper(IrodsEntityMapper[DataObject], metaclass=ABCMeta):
    """
    iRODS data object mapper.
    """


class CollectionMapper(IrodsEntityMapper[Collection], metaclass=ABCMeta):
    """
    iRODS collection mapper.
    """


class CustomObjectMapper(Generic[CustomObjectType], metaclass=ABCMeta):
    """
    Mapper for a custom object, retrieved from iRODS using a pre-installed specific query.
    """
    @abstractmethod
    def _get_with_prepared_specific_query(self, specific_query: PreparedSpecificQuery, zone: str=None) \
            -> Sequence[CustomObjectType]:
        """
        Gets an object from iRODS using a specific query.
        :param specific_query: the specific query to use
        :param zone: limit query to specific zone in iRODS
        :return: Python model of the object returned from iRODS using the specific query
        """


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
