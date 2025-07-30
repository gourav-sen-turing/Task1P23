from omymodels.types import (
    populate_types_mapping,
    datetime_types,
    json_types,
    string_types,
    integer_types,
    big_integer_types,
    float_types,
    numeric_types,
    boolean_types,
)

mapper = {
    string_types: "string",
    integer_types: "integer",
    big_integer_types: "bigint",
    float_types: "float",
    numeric_types: "decimal",
    boolean_types: "boolean",
    datetime_types: "datetime",
    json_types: "json",
}

types_mapping = populate_types_mapping(mapper)

direct_types = {
    "date": "date",
    "timestamp": "datetime",
    "text": "text",
    "smallint": "integer",
    "jsonb": "json",
    "uuid": "string",
}


types_mapping.update(direct_types)
