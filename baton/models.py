from enum import Enum

from typing import List


class ComparisonOperator(Enum):
    EQUALS = "=",
    LESS_THAN = "<"
    GREATER_THAN = ">"


class SearchCriteria(list):
    def append(self, search_criterion: SearchCriterion):
        for existing_search_criterion in self:
            if existing_search_criterion.attribute == search_criterion.attribute:
                raise ValueError("Search criterion based on the attribute `%s` already added")

        super(SearchCriteria, self).append(search_criterion)


class SearchCriterion:
    def __init__(self, attribute: str, value: str, comparison_operator: ComparisonOperator):
        self.attribute = attribute
        self.value = value
        self.comparison_operator = comparison_operator


class AttributeSearch:
    def __init__(self, search_criteria: List[SearchCriterion]):
        self.search_criteria = search_criteria


class IrodsFileLocation:
    def __init__(self, directory: str, file_name: str):
        self.directory = directory
        self.file_name = file_name
