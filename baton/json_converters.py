from baton.models import IrodsFileLocation, AttributeSearch, SearchCriterion, ComparisonOperator


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


def object_to_baton_json(obj: object):
    """
    TODO
    :param obj:
    :return:
    """
    if obj.__class__ not in _MAPPINGS:
        raise ValueError("Cannot convert object of type `%s`" % obj.__class__)

    return _MAPPINGS[obj.__class__](obj)


def _search_criterion_to_baton_json(search_criteria: SearchCriterion) -> dict:
    """
    TODO
    :param search_criteria:
    :return:
    """
    return {
        _BATON_ATTRIBUTE_PROPERTY: search_criteria.attribute,
        _BATON_VALUE_PROPERTY: search_criteria.value,
        _BATON_COMPARISON_OPERATOR_PROPERTY: _BATON_COMPARISON_OPERATORS[search_criteria.comparison_operator]
    }


def _attribute_search_to_baton_json(attribute_search: AttributeSearch) -> dict:
    """
    TODO
    :param attribute_search:
    :return:
    """
    search_matches_as_baton_json_list = []

    for criterion in attribute_search.search_criteria:
        search_match_as_baton_json = _search_criterion_to_baton_json(criterion)
        search_matches_as_baton_json_list.append(search_match_as_baton_json)

    return {
        _BATON_AVU_SEARCH_PROPERTY: search_matches_as_baton_json_list
    }


def _irods_file_location_to_baton_json(irods_file_location: IrodsFileLocation) -> dict:
    """
    TODO
    :param irods_file_location:
    :return:
    """
    return {
        _BATON_FILE_NAME_PROPERTY: irods_file_location.file_name,
        _BATON_DIRECTORY_PROPERTY: irods_file_location.directory
    }


_MAPPINGS = {
    SearchCriterion: _search_criterion_to_baton_json,
    AttributeSearch: _attribute_search_to_baton_json,
    IrodsFileLocation: _irods_file_location_to_baton_json
}
