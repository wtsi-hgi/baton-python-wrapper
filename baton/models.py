from typing import List

from baton.enums import ComparisonOperator


class SearchCriterion:
    """
    Model of an attribute search criterion.
    """
    def __init__(self, attribute: str, value: str, comparison_operator: ComparisonOperator):
        self.attribute = attribute
        self.value = value
        self.comparison_operator = comparison_operator


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


class IrodsFileLocation:
    """
    Model of an iRODS file location.
    """
    def __init__(self, directory: str, file_name: str):
        self.directory = directory
        self.file_name = file_name
