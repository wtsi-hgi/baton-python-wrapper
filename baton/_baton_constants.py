from hgicommon.enums import ComparisonOperator


BATON_FILE_NAME_PROPERTY = "data_object"
BATON_DIRECTORY_PROPERTY = "collection"
BATON_FILE_CHECKSUM_PROPERTY = "checksum"
BATON_FILE_REPLICATE_PROPERTY = "replicate"
BATON_FILE_REPLICATE_ID_PROPERTY = "number"
BATON_METADATA_PROPERTY = "avus"

BATON_ATTRIBUTE_PROPERTY = "attribute"
BATON_VALUE_PROPERTY = "value"
BATON_COMPARISON_OPERATOR_PROPERTY = "o"

BATON_AVU_SEARCH_PROPERTY = "avus"

BATON_COMPARISON_OPERATORS = {
    ComparisonOperator.EQUALS: "=",
    ComparisonOperator.GREATER_THAN: ">",
    ComparisonOperator.LESS_THAN: "<"
}
