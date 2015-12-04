from abc import ABCMeta, abstractmethod
from typing import List
from typing import Union

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion, File

from baton.models import IrodsFile


class IrodsMapper(metaclass=ABCMeta):
    """
    Superclass that all iRODS mappers should extend.

    A data metadata_mapper as defined by Martin Fowler (see: http://martinfowler.com/eaaCatalog/dataMapper.html) that
    moves data between objects and iRODS, while keeping them independent of each other and the metadata_mapper itself.
    """
    pass


class IrodsFileMapper(IrodsMapper, metaclass=ABCMeta):
    """
    iRODS file mapper.
    """
    @abstractmethod
    def get_by_metadata(self, metadata_search_criteria: Union[SearchCriterion, SearchCriteria],
                        load_metadata: bool=False) -> List[IrodsFile]:
        """
        Gets files from iRODS that have metadata that matches the given search criteria.
        :param metadata_search_criteria: the metadata search criteria
        :param load_metadata: whether the file's associated metadata should also be loaded
        :return: the matched files in iRODS
        """
        pass

    @abstractmethod
    def get_by_path(self, files: Union[File, List[File]], load_metadata: bool=True) -> List[IrodsFile]:
        """
        Gets information about the given files from iRODS.

        If one or more of the files does not exist, a `FileNotFound` exception will be raised.
        :param files: the files to get from iRODS
        :param load_metadata: whether metadata associated to the files should be loaded
        :return: the file information loaded from iRODS
        """
        pass

    @abstractmethod
    def get_in_collection(self, collections: Union[str, List[str]], load_metadata: bool=True) -> List[IrodsFile]:
        """
        Gets information about files in the given iRODS collections.

        TODO: Is the below true?
        If one or more of the collections does not exist, a `FileNotFound` exception will be raised.
        :param collections: the collections to get the files from
        :param load_metadata: whether metadata associated to the files should be loaded
        :return: the file information loaded from iRODS
        """
        pass
