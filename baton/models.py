from abc import ABCMeta
from typing import List

from baton.enums import ComparisonOperator


class Model(metaclass=ABCMeta):
    """
    Superclass that all POPOs (Plain Old Python Objects) must implement.
    """
    def __init__(self, *args, **kwargs):
        pass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for property, value in vars(self).items():
            if other.__dict__[property] != self.__dict__[property]:
                return False
        return True

    def __str__(self) -> str:
        string_builder = []
        for property, value in vars(self).items():
            string_builder.append("%s: %s" % (property, value))
        return "{ %s }" % ', '.join(string_builder)


class SearchCriterion(Model):
    """
    Model of an attribute search criterion.
    """
    def __init__(self, attribute: str, value: str, comparison_operator: ComparisonOperator):
        super(SearchCriterion, self).__init__()
        self.attribute = attribute
        self.value = value
        self.comparison_operator = comparison_operator


class IrodsFileLocation(Model):
    """
    Model of an iRODS file location.
    """
    def __init__(self, directory: str, file_name: str):
        super(IrodsFileLocation, self).__init__()
        self.directory = directory
        self.file_name = file_name


class SearchCriteria(list):
    """
    A collection of `SearchCriteria`.
    """
    def __init__(self, search_criterion_list: List[SearchCriterion]=()):
        super(SearchCriteria, self).__init__()
        for search_criterion in search_criterion_list:
            self.append(search_criterion)

    def append(self, search_criterion: SearchCriterion):
        for existing_search_criterion in self:
            if existing_search_criterion.attribute == search_criterion.attribute:
                raise ValueError("Search criterion based on the attribute `%s` already added")

        super(SearchCriteria, self).append(search_criterion)
