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

    Raises a value error if conversion is not possible
    :param obj: the object to convert to a baton representation
    :return: the baton JSON representation of the given object
    """
    if obj.__class__ not in _OBJECT_TO_JSON_BATON_CONVERTERS:
        raise ValueError("Cannot convert object of type `%s`" % obj.__class__)

    return _OBJECT_TO_JSON_BATON_CONVERTERS[obj.__class__](obj)


def baton_json_to_object(baton_json: dict, target_model: type) -> object:
    """
    Converts a given baton JSON object to the given target model type.

    Raises a value error if unsupported target type is given or if conversion is not possible
    :param baton_json: the JSON representation of the object used by baton
    :param target_model: the model to create from the given JSON
    :return: model of the baton JSON of the type specified by `target_model`
    """
    if target_model not in _BATON_JSON_TO_OBJECT_CONVERTERS:
        raise ValueError("Cannot convert object of type `%s`" % target_model)

    return _BATON_JSON_TO_OBJECT_CONVERTERS[target_model](baton_json)


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


def _baton_json_to_search_criterion(baton_json: dict) -> SearchCriterion:
    """
    Converts a given baton JSON representation of a search criterion to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    for operator_enum, operator_symbol in _BATON_COMPARISON_OPERATORS.items():
        if operator_symbol == baton_json[_BATON_COMPARISON_OPERATOR_PROPERTY]:
            return SearchCriterion(
                baton_json[_BATON_ATTRIBUTE_PROPERTY],
                baton_json[_BATON_VALUE_PROPERTY],
                operator_enum
            )
    raise ValueError("Could not convert baton JSON to a `SearchCriterion` model:\n%s" % baton_json)


def _baton_json_to_search_criteria(baton_json: dict) -> SearchCriteria:
    """
    Converts a given baton JSON representation of a search criteria to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    search_matches = []
    for search_match_as_baton_json in baton_json[_BATON_AVU_SEARCH_PROPERTY]:
        search_match = _baton_json_to_search_criterion(search_match_as_baton_json)
        search_matches.append(search_match)

    return SearchCriteria(search_matches)


def _baton_json_to_irods_file(baton_json: dict) -> IrodsFile:
    """
    Converts a given baton JSON representation of a iRODS file to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return IrodsFile(
        baton_json[_BATON_DIRECTORY_PROPERTY],
        baton_json[_BATON_FILE_NAME_PROPERTY]
    )


# Mappings between models and the methods that can create baton JSON representations of them
_OBJECT_TO_JSON_BATON_CONVERTERS = {
    SearchCriterion: _search_criterion_to_baton_json,
    SearchCriteria: _search_criteria_to_baton_json,
    IrodsFile: _irods_file_to_baton_json
}


# Mappings between required models and the mapping method that convert JSON representations to the models
_BATON_JSON_TO_OBJECT_CONVERTERS = {
    SearchCriterion: _baton_json_to_search_criterion,
    SearchCriteria: _baton_json_to_search_criteria,
    IrodsFile: _baton_json_to_irods_file
}