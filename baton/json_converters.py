from baton.models import IrodsFileLocation, AttributeSearch, SearchMatch, ComparisonOperator


_BATON_DATA_OBJECT_PROPERTY = "data_object"
_BATON_COLLECTION_PROPERTY = "collection"

_BATON_ATTRIBUTE_PROPERTY = "attribute"
_BATON_VALUE_PROPERTY = "value"
_BATON_COMPARISON_OPERATOR_PROPERTY = "o"

_BATON_AVU_SEARCH_PROPERTY = "avus"

_BATON_COMPARISON_OPERATORS = {
    "=": ComparisonOperator.EQUALS,
    ">": ComparisonOperator.GREATER_THAN,
    "<": ComparisonOperator.LESS_THAN
}


def baton_json_to_object(baton_json: dict, target_model: type) -> object:
    """
    Converts a given baton JSON object to the given target model type.

    Raises a value error if unsupported target type is given or if conversion is not possible
    :param baton_json: the JSON representation of the object used by baton
    :param target_model: the model to create from the given JSON
    :return: model of the baton JSON of the type specified by `target_model`
    """
    if target_model not in _MAPPINGS:
        raise ValueError("Cannot convert object of type `%s`" % target_model)

    return _MAPPINGS[target_model](baton_json)


def _baton_json_to_search_match(baton_json: dict) -> SearchMatch:
    """
    Converts a given baton JSON representation of a search match to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return SearchMatch(
        baton_json[_BATON_ATTRIBUTE_PROPERTY],
        baton_json[_BATON_VALUE_PROPERTY],
        _BATON_COMPARISON_OPERATORS[_BATON_COMPARISON_OPERATOR_PROPERTY]
    )


def _baton_json_to_attribute_search(baton_json: dict) -> AttributeSearch:
    """
    Converts a given baton JSON representation of an attribute search to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    search_matches = []
    for search_match_as_baton_json in baton_json[_BATON_AVU_SEARCH_PROPERTY]:
        search_match = _baton_json_to_search_match(search_match_as_baton_json)
        search_matches.append(search_match)

    return AttributeSearch(search_matches)


def _baton_json_to_irods_file_location(baton_json: dict) -> IrodsFileLocation:
    """
    Converts a given baton JSON representation of a iRODS file location to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return IrodsFileLocation(
        baton_json[_BATON_DATA_OBJECT_PROPERTY],
        baton_json[_BATON_COLLECTION_PROPERTY]
    )


def object_to_baton_json(obj: object):
    pass




_MAPPINGS = {
    SearchMatch: _baton_json_to_attribute_search,
    AttributeSearch: _baton_json_to_attribute_search,
    IrodsFileLocation: _baton_json_to_irods_file_location
}


