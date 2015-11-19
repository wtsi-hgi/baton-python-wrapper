from abc import ABCMeta, abstractmethod
from typing import Union

from typing import List

from baton.models import Metadata, SearchCriteria, SearchCriterion, IrodsFile


class IrodsMapper(metaclass=ABCMeta):
    """
    Superclass that all iRODS mappers should extend.

    A data mapper as defined by Martin Fowler (see: http://martinfowler.com/eaaCatalog/dataMapper.html) that moves data
    between objects and iRODS, while keeping them independent of each other and the mapper itself.
    """
    pass


class IrodsMetadataMapper(IrodsMapper, metaclass=ABCMeta):
    """
    iRODS metadata mapper.
    """
    @abstractmethod
    def _run_baton_metadata_query(self, baton_json):
        """
        Run a baton attribute value query defined by the given JSON.
        :param baton_json: the JSON that defines the query
        :return: the return from baton
        """
        pass

    @abstractmethod
    def get_for_file(self, file_paths: Union[str, List[str]]) -> List[Metadata]:
        """
        Gets the metadata in iRODS for the file with at the given path.
        :param file_paths: the path of the file in iRODS
        :return: the metadata associated with the file
        """
        pass

    @abstractmethod
    def get_by_attribute(self, search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[Metadata]:
        """
        Gets metadata in iRODS that matches one or more of the given attribute search criteria.
        :param search_criteria: the search criteria to get metadata by
        :return: metadata that matches the given search criteria
        """
        pass


class IrodsFileMapper(IrodsMapper, metaclass=ABCMeta):
    """
    iRODS file mapper.
    """
    @abstractmethod
    def get_by_metadata_attribute(
            self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria]) -> List[IrodsFile]:
        """
        Gets files from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :return: the matched files in iRODS
        """
        pass
