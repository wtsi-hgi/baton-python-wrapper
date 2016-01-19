from hgicommon.collections import SearchCriteria

from baton._constants import BATON_ATTRIBUTE_PROPERTY, BATON_COMPARISON_OPERATOR_PROPERTY, \
    BATON_COMPARISON_OPERATORS, BATON_AVU_SEARCH_PROPERTY, BATON_DATA_OBJECT_PROPERTY, BATON_COLLECTION_PROPERTY, \
    BATON_METADATA_PROPERTY, BATON_SPECIFIC_QUERY_PROPERTY, BATON_SPECIFIC_QUERY_ARGUMENTS_PROPERTY, \
    BATON_SPECIFIC_QUERY_SQL_PROPERTY, BATON_VALUE_PROPERTY
from baton.models import DataObject, Collection, IrodsMetadata, PreparedSpecificQuery


def search_criteria_to_baton_json(search_criteria: SearchCriteria) -> dict:
    """
    Creates a baton JSON representation of the given search criteria.
    :param search_criteria: the search criteria to convert to a baton representation
    :return: the baton JSON representation of the given search criteria
    """
    search_criteria_as_baton_json_list = []

    for search_criterion in search_criteria:
        search_match_as_baton_json = {
            BATON_ATTRIBUTE_PROPERTY: search_criterion.attribute,
            BATON_VALUE_PROPERTY: search_criterion.value,
            BATON_COMPARISON_OPERATOR_PROPERTY: BATON_COMPARISON_OPERATORS[search_criterion.comparison_operator]
        }
        search_criteria_as_baton_json_list.append(search_match_as_baton_json)
    return {
        BATON_AVU_SEARCH_PROPERTY: search_criteria_as_baton_json_list
    }


def data_object_to_baton_json(data_object: DataObject) -> dict:
    """
    Creates a baton representation of the given iRODS data object (i.e. iRODS "file").
    :param data_object: the data object
    :return: the baton JSON representation of the data object
    """
    return {
        BATON_COLLECTION_PROPERTY: data_object.get_collection_path(),
        BATON_DATA_OBJECT_PROPERTY: data_object.get_name()
    }


def collection_to_baton_json(collection: Collection) -> dict:
    """
    Creates a baton representation of the given iRODS collection (i.e. iRODS "folder").
    :param collection: the collection
    :return: the baton JSON representation of the collection
    """
    return {
        BATON_COLLECTION_PROPERTY: collection.path
    }


def irods_metadata_to_baton_json(metadata: IrodsMetadata) -> dict:
    """
    Creates a baton JSON representation of the given collection of metadata.
    :param metadata: the collection of metadata
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


def prepared_specific_query_to_baton_json(prepared_specific_query: PreparedSpecificQuery) -> dict:
    """
    Creates a baton JSON representation of the given specific query.
    :param prepared_specific_query: the specific query
    :return: the baton JSON representation of the given specific query
    """
    return {
        BATON_SPECIFIC_QUERY_PROPERTY: {
            BATON_SPECIFIC_QUERY_SQL_PROPERTY: prepared_specific_query.alias,
            BATON_SPECIFIC_QUERY_ARGUMENTS_PROPERTY: prepared_specific_query.query_arguments
        }
    }
