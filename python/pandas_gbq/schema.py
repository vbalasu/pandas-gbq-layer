"""Helper methods for BigQuery schemas"""

import copy


def to_pandas_gbq(client_schema):
    """Given a sequence of :class:`google.cloud.bigquery.schema.SchemaField`,
    return a schema in pandas-gbq API format.
    """
    remote_fields = [
        field_remote.to_api_repr() for field_remote in client_schema
    ]
    for field in remote_fields:
        field["type"] = field["type"].upper()
        field["mode"] = field["mode"].upper()

    return {"fields": remote_fields}


def _clean_schema_fields(fields):
    """Return a sanitized version of the schema for comparisons.

    The ``mode`` and ``description`` properties areis ignored because they
    are not generated by func:`pandas_gbq.schema.generate_bq_schema`.
    """
    fields_sorted = sorted(fields, key=lambda field: field["name"])
    return [
        {"name": field["name"], "type": field["type"]}
        for field in fields_sorted
    ]


def schema_is_subset(schema_remote, schema_local):
    """Indicate whether the schema to be uploaded is a subset

    Compare the BigQuery table identified in the parameters with
    the schema passed in and indicate whether a subset of the fields in
    the former are present in the latter. Order is not considered.

    Parameters
    ----------
    schema_remote : dict
        Schema for comparison. Each item of ``fields`` should have a 'name'
        and a 'type'
    schema_local : dict
        Schema for comparison. Each item of ``fields`` should have a 'name'
        and a 'type'

    Returns
    -------
    bool
        Whether the passed schema is a subset
    """
    fields_remote = _clean_schema_fields(schema_remote.get("fields", []))
    fields_local = _clean_schema_fields(schema_local.get("fields", []))
    return all(field in fields_remote for field in fields_local)


def generate_bq_schema(dataframe, default_type="STRING"):
    """Given a passed dataframe, generate the associated Google BigQuery schema.

    Arguments:
        dataframe (pandas.DataFrame): D
    default_type : string
        The default big query type in case the type of the column
        does not exist in the schema.
    """

    # If you update this mapping, also update the table at
    # `docs/source/writing.rst`.
    type_mapping = {
        "i": "INTEGER",
        "b": "BOOLEAN",
        "f": "FLOAT",
        "O": "STRING",
        "S": "STRING",
        "U": "STRING",
        "M": "TIMESTAMP",
    }

    fields = []
    for column_name, dtype in dataframe.dtypes.iteritems():
        fields.append(
            {
                "name": column_name,
                "type": type_mapping.get(dtype.kind, default_type),
            }
        )

    return {"fields": fields}


def update_schema(schema_old, schema_new):
    """
    Given an old BigQuery schema, update it with a new one.

    Where a field name is the same, the new will replace the old. Any
    new fields not present in the old schema will be added.

    Arguments:
        schema_old: the old schema to update
        schema_new: the new schema which will overwrite/extend the old
    """
    old_fields = schema_old["fields"]
    new_fields = schema_new["fields"]
    output_fields = list(old_fields)

    field_indices = {field["name"]: i for i, field in enumerate(output_fields)}

    for field in new_fields:
        name = field["name"]
        if name in field_indices:
            # replace old field with new field of same name
            output_fields[field_indices[name]] = field

    return {"fields": output_fields}


def add_default_nullable_mode(schema):
    """Manually create the schema objects, adding NULLABLE mode."""
    # Workaround for:
    # https://github.com/GoogleCloudPlatform/google-cloud-python/issues/4456
    #
    # Returns a copy rather than modifying the mutable arg,
    # per Issue #277
    result = copy.deepcopy(schema)
    for field in result["fields"]:
        field.setdefault("mode", "NULLABLE")
    return result