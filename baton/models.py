from enum import Enum

from typing import List


class ComparisonOperator(Enum):
    EQUALS = "=",
    LESS_THAN = "<"
    GREATER_THAN = ">"


class SearchMatch:
    def __init__(self, attribute: str, value: str, comparison_operator: ComparisonOperator):
        self.attribute = attribute
        self.value = value
        self.comparison_operator = comparison_operator


class AttributeSearch:
    def __init__(self, search_match: List[SearchMatch]):
        self.search_match = search_match


class IrodsFileLocation:
    def __init__(self, directory: str, file_name: str):
        self.directory = directory
        self.file_name = file_name
