from typing import List, GenericMeta, Union

from hgicommon.collections import SearchCriteria
from hgicommon.models import SearchCriterion, Model

from baton._baton_constants import BATON_ATTRIBUTE_PROPERTY, BATON_COMPARISON_OPERATOR_PROPERTY, \
    BATON_COMPARISON_OPERATORS, BATON_DIRECTORY_PROPERTY, BATON_FILE_NAME_PROPERTY, BATON_FILE_CHECKSUM_PROPERTY, \
    BATON_METADATA_PROPERTY, BATON_AVU_SEARCH_PROPERTY, BATON_FILE_REPLICATE_PROPERTY, BATON_FILE_REPLICATE_ID_PROPERTY
from baton._baton_constants import BATON_VALUE_PROPERTY
from baton.models import IrodsFile, IrodsMetadata, IrodsFileReplica


def baton_json_to_model(baton_json: dict, target_model: type) -> Union[Model, List[Model]]:
    """
    Converts a given baton JSON object to the given target model type.

    Raises a value error if unsupported target type is given or if conversion is not possible
    :param baton_json: the JSON representation of the object used by baton
    :param target_model: the model to create from the given JSON. Can be an list of models
    :return: model of the baton JSON of the type specified by `target_model`
    """
    if isinstance(target_model, GenericMeta):
        if "List" not in repr(target_model):
            raise ValueError("Only generic type permitted is `List`")
        models = []
        for baton_json_item in baton_json:
            models.append(baton_json_to_model(baton_json_item, target_model.__parameters__[0]))
        return models
    else:
        if target_model not in _BATON_JSON_TO_OBJECT_CONVERTERS:
            raise ValueError("Cannot convert object of type `%s`" % target_model)
        return _BATON_JSON_TO_OBJECT_CONVERTERS[target_model](baton_json)


def _baton_json_to_search_criterion(baton_json: dict) -> SearchCriterion:
    """
    Converts a given baton JSON representation of a search criterion to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    for operator_enum, operator_symbol in BATON_COMPARISON_OPERATORS.items():
        if operator_symbol == baton_json[BATON_COMPARISON_OPERATOR_PROPERTY]:
            return SearchCriterion(
                baton_json[BATON_ATTRIBUTE_PROPERTY],
                baton_json[BATON_VALUE_PROPERTY],
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
    for search_match_as_baton_json in baton_json[BATON_AVU_SEARCH_PROPERTY]:
        search_match = _baton_json_to_search_criterion(search_match_as_baton_json)
        search_matches.append(search_match)

    return SearchCriteria(search_matches)


def _baton_json_to_irods_file(baton_json: dict) -> IrodsFile:
    """
    Converts a given baton JSON representation of a iRODS file to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    if BATON_FILE_REPLICATE_PROPERTY in baton_json:
        replicas = baton_json_to_model(baton_json[BATON_FILE_REPLICATE_PROPERTY], List[IrodsFileReplica])
    else:
        replicas = []

    metadata = None
    if BATON_METADATA_PROPERTY in baton_json:
        metadata = baton_json_to_model(baton_json[BATON_METADATA_PROPERTY], List[IrodsMetadata])

    return IrodsFile(
        baton_json[BATON_DIRECTORY_PROPERTY],
        baton_json[BATON_FILE_NAME_PROPERTY],
        baton_json[BATON_FILE_CHECKSUM_PROPERTY],
        replicas,
        metadata
    )


def _baton_json_to_irods_file_replica(baton_json: dict) -> IrodsFileReplica:
    """
    Converts a given baton JSON representation of a iRODS file replica to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    return IrodsFileReplica(
        baton_json[BATON_FILE_REPLICATE_ID_PROPERTY],
        baton_json[BATON_FILE_CHECKSUM_PROPERTY]
    )


def _baton_json_to_irods_metadata(baton_json: dict) -> IrodsMetadata:
    """
    Converts a given baton JSON representation of collection of metadata to the corresponding model.
    :param baton_json: the JSON representation of the object used by baton
    :return: the corresponding model
    """
    metadata_items_as_json = baton_json[BATON_METADATA_PROPERTY]
    metadata = IrodsMetadata()
    for metadatum in metadata_items_as_json:
        assert len(list(metadatum.keys())) == 2
        key = metadatum[BATON_ATTRIBUTE_PROPERTY]
        value = metadatum[BATON_VALUE_PROPERTY]
        if key not in metadata:
            metadata[key] = [value]
        else:
            metadata[key].append(value)
    return metadata


# Mappings between required models and the mapping method that convert JSON representations to the models
_BATON_JSON_TO_OBJECT_CONVERTERS = {
    SearchCriterion: _baton_json_to_search_criterion,
    SearchCriteria: _baton_json_to_search_criteria,
    IrodsFile: _baton_json_to_irods_file,
    IrodsMetadata: _baton_json_to_irods_metadata,
    IrodsFileReplica: _baton_json_to_irods_file_replica
}
