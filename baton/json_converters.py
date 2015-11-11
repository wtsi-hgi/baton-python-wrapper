from baton.enums import ComparisonOperator
from baton.models import IrodsFile, SearchCriterion, SearchCriteria


_BATON_FILE_NAME_PROPERTY = "data_object"
_BATON_DIRECTORY_PROPERTY = "collection"

_BATON_ATTRIBUTE_PROPERTY = "attribute"
_BATON_VALUE_PROPERTY = "value"
_BATON_COMPARISON_OPERATOR_PROPERTY = "o"

_BATON_AVU_SEARCH_PROPERTY = "avus"

_BATON_COMPARISON_OPERATORS = {
    ComparisonOperator.EQUALS: "=",
    ComparisonOperator.GREATER_THAN: ">",
    ComparisonOperator.LESS_THAN: "<"
}


def object_to_baton_json(obj: object) -> dict:
    """
    Creates a baton JSON representation of the given object.
    :param obj: the object to convert to a baton representation
    :return: the baton JSON representation of the given object
    """
    if obj.__class__ not in _MAPPINGS:
        raise ValueError("Cannot convert object of type `%s`" % obj.__class__)

    return _MAPPINGS[obj.__class__](obj)


def _search_criterion_to_baton_json(search_criterion: SearchCriterion) -> dict:
    """
    Creates a baton JSON representation of the given search criterion.
    :param search_criterion: the search criterion to convert to a baton representation
    :return: the baton JSON representation of the given search criterion
    """
    return {
        _BATON_ATTRIBUTE_PROPERTY: search_criterion.attribute,
        _BATON_VALUE_PROPERTY: search_criterion.value,
        _BATON_COMPARISON_OPERATOR_PROPERTY: _BATON_COMPARISON_OPERATORS[search_criterion.comparison_operator]
    }


def _search_criteria_to_baton_json(search_criteria: SearchCriteria) -> dict:
    """
    Creates a baton JSON representation of the given search criteria.
    :param search_criteria: the search criteria to convert to a baton representation
    :return: the baton JSON representation of the given search criteria
    """
    search_criteria_as_baton_json_list = []

    for criterion in search_criteria:
        search_match_as_baton_json = _search_criterion_to_baton_json(criterion)
        search_criteria_as_baton_json_list.append(search_match_as_baton_json)
    return {
        _BATON_AVU_SEARCH_PROPERTY: search_criteria_as_baton_json_list
    }


def _irods_file_to_baton_json(irods_file: IrodsFile) -> dict:
    """
     Creates a baton JSON representation of the given iRODS file.
    :param irods_file: the iRODS file to convert to a baton representation
    :return: the baton JSON representation of the given iRODS file
    """
    return {
        _BATON_FILE_NAME_PROPERTY: irods_file.file_name,
        _BATON_DIRECTORY_PROPERTY: irods_file.directory
    }


# Mappings between models and the methods that can create baton JSON representations of them
_MAPPINGS = {
    SearchCriterion: _search_criterion_to_baton_json,
    SearchCriteria: _search_criteria_to_baton_json,
    IrodsFile: _irods_file_to_baton_json
}
