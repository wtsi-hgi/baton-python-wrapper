from abc import ABCMeta, abstractmethod
from typing import List
from typing import Union

from hgicommon.collections import SearchCriteria, Metadata
from hgicommon.models import SearchCriterion

from baton.models import IrodsFile


class IrodsMapper(metaclass=ABCMeta):
    """
    Superclass that all iRODS mappers should extend.

    A data metadata_mapper as defined by Martin Fowler (see: http://martinfowler.com/eaaCatalog/dataMapper.html) that
    moves data between objects and iRODS, while keeping them independent of each other and the metadata_mapper itself.
    """
    pass


class IrodsMetadataMapper(IrodsMapper, metaclass=ABCMeta):
    """
    iRODS metadata metadata_mapper.
    """
    @abstractmethod
    def get_for_file(self, file_paths: Union[str, List[str]]) -> Metadata:
        """
        Gets the metadata in iRODS for the file with at the given path.
        :param file_paths: the path of the file in iRODS
        :return: the metadata associated with the file
        """
        pass


class IrodsFileMapper(IrodsMapper, metaclass=ABCMeta):
    """
    iRODS file metadata_mapper.
    """
    @abstractmethod
    def get_by_metadata_attribute(self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria],
                                  load_metadata: bool=False) -> List[IrodsFile]:
        """
        Gets files from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :param load_metadata: whether the file's associated metadata should also be loaded
        :return: the matched files in iRODS
        """
        pass
