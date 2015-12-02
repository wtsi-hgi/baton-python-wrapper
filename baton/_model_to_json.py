from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion, File

from baton import IrodsMetadata, IrodsFile
from baton._baton_constants import BATON_ATTRIBUTE_PROPERTY, BATON_COMPARISON_OPERATOR_PROPERTY, \
    BATON_COMPARISON_OPERATORS, BATON_AVU_SEARCH_PROPERTY, BATON_FILE_NAME_PROPERTY, BATON_DIRECTORY_PROPERTY, \
    BATON_METADATA_PROPERTY
from baton._baton_constants import BATON_VALUE_PROPERTY


def model_to_baton_json(objects: object) -> dict:
    """
    Creates a baton JSON representation of the given object.

    Raises a value error if conversion is not possible
    :param objects: the object to convert to a baton representation
    :return: the baton JSON representation of the given object
    """
    if objects.__class__ not in _OBJECT_TO_JSON_BATON_CONVERTERS:
        raise ValueError("Cannot convert object of type `%s`" % objects.__class__)

    return _OBJECT_TO_JSON_BATON_CONVERTERS[objects.__class__](objects)


def _search_criterion_to_baton_json(search_criterion: SearchCriterion) -> dict:
    """
    Creates a baton JSON representation of the given search criterion.
    :param search_criterion: the search criterion to convert to a baton representation
    :return: the baton JSON representation of the given search criterion
    """
    return {
        BATON_ATTRIBUTE_PROPERTY: search_criterion.attribute,
        BATON_VALUE_PROPERTY: search_criterion.value,
        BATON_COMPARISON_OPERATOR_PROPERTY: BATON_COMPARISON_OPERATORS[search_criterion.comparison_operator]
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
        BATON_AVU_SEARCH_PROPERTY: search_criteria_as_baton_json_list
    }


def _file_to_baton_json(irods_file: File) -> dict:
    """
    Creates a baton JSON representation of the given iRODS file.
    :param irods_file: the iRODS file to convert to a baton representation
    :return: the baton JSON representation of the given iRODS file
    """
    return {
        BATON_FILE_NAME_PROPERTY: irods_file.file_name,
        BATON_DIRECTORY_PROPERTY: irods_file.directory
    }


def _irods_metadata_to_baton_json(metadata: IrodsMetadata) -> dict:
    """
    Creates a baton JSON representation of the given collection of metadata.
    :param metadata: the collection of metadata to convert to a baton representation
    :return: the baton JSON representation of the given metadata
    """
    metadata_items_as_json = []
    for key, values in metadata.items():
        for value in values:
            metadata_items_as_json.append({
                BATON_ATTRIBUTE_PROPERTY: key,
                BATON_VALUE_PROPERTY: value
            })
    return {
        BATON_METADATA_PROPERTY: metadata_items_as_json
    }


# Mappings between models and the methods that can create baton JSON representations of them
_OBJECT_TO_JSON_BATON_CONVERTERS = {
    SearchCriterion: _search_criterion_to_baton_json,
    SearchCriteria: _search_criteria_to_baton_json,
    File: _file_to_baton_json,
    IrodsFile: _file_to_baton_json,
    IrodsMetadata: _irods_metadata_to_baton_json
}