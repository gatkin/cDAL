"""Contains functionality for parsing cDAL dataset definitions"""
import json
import jsonschema
import re
import dataset


_SCHEMA_FILE_PATH = 'dataset.schema.json'

# Query parameters are specified in the format 'WHERE id = {model_id:PrimaryKey}'
_QUERY_PARAMETER_PATTERN = r'{(\w+):(\w+)}'
_QUERY_PARAMETER_RE = re.compile(_QUERY_PARAMETER_PATTERN)


class DatasetDefinitionError(Exception):
    """Base class for exceptions related to invalid dataset defintions"""
    pass


def dataset_from_definition(definition):
    """Parses the provided dataset from the definition dictionary"""
    _validate_definition(definition)

    name = definition['datasetName']
    models = [_model_from_definition(model_definition) for model_definition in definition['models']]

    return dataset.Dataset(name, models)


def _validate_definition(definition):
    """Validates the provided definition dictionary against the dataset definition schema"""
    with open(_SCHEMA_FILE_PATH) as schema_file:
        schema = json.load(schema_file)

    try:
        jsonschema.validate(definition, schema)
    except jsonschema.ValidationError as validation_error:
        raise DatasetDefinitionError('Invalid dataset definition: ' + validation_error.message)

    return definition


def _model_from_definition(model_definition):
    """Parses the given model definition dictionary into a Model"""
    name = model_definition['name']

    # Get the values for the optional fields
    type_name = model_definition.get('typeName')
    table_name = model_definition.get('tableName')

    fields = [_field_from_definition(field_definition) for field_definition in model_definition['fields']]

    if 'queries' in model_definition:
        queries = _queries_from_definition(model_definition['queries'])
    else:
        queries = []

    return dataset.Model(name, fields, queries, type_name, table_name)


def _field_from_definition(field_definition):
    """Parses the model field from field definition dictionary"""
    name = field_definition['name']
    field_type = _field_type_get(field_definition['type'])
    max_length = _field_max_length_get(field_type, field_definition)

    return dataset.ModelField(name, field_type, max_length)


def _field_type_get(input_field_type):
    """Parses field type from field type specified in the definition"""
    try:
        matching_type, = [field_type for field_type in dataset.ModelFieldType
                          if field_type.value == input_field_type]
    except ValueError:
        raise DatasetDefinitionError('Invalid field type: ' + input_field_type)

    return matching_type


def _field_max_length_get(field_type, field_definition):
    """Gets the max length for field"""
    max_length_key = 'maxLength'
    max_length = 0

    if max_length_key in field_definition:
        if not _field_type_can_have_max_length(field_type):
            raise DatasetDefinitionError('Fields of type {} cannot have a max length'.
                                         format(field_type.value))

        max_length = field_definition[max_length_key]
        if max_length <= 0:
            raise DatasetDefinitionError('Invalid max length value: ' + max_length)

    return max_length


def _field_type_can_have_max_length(field_type):
    """Returns True if the given ModelFieldType can have a maximum length attribute"""
    return field_type in {dataset.ModelFieldType.TEXT, dataset.ModelFieldType.BLOB}


def _queries_from_definition(query_defs):
    """Parses all model queries defined for a model"""
    query_types = {
        'count': dataset.ModelQueryType.COUNT,
        'delete': dataset.ModelQueryType.DELETE,
        'find': dataset.ModelQueryType.FIND,
        'select': dataset.ModelQueryType.SELECT,
        'update': dataset.ModelQueryType.UPDATE,
    }
    queries = []
    for query_type_key in query_defs:
        if query_type_key not in query_types:
            raise DatasetDefinitionError('Invalid query type: ' + query_type_key)

        query_type = query_types[query_type_key]
        queries += [_query_from_definition(query_type, query_def)
                    for query_def in query_defs[query_type_key]]

    return queries


def _query_from_definition(query_type, query_def):
    """Parses the provided query definition dictionary"""
    name = query_def['name']
    query_def_string = query_def['query']
    query_string = _query_def_remove_param_defs(query_def_string)
    parameters = _query_parameters_from_definition(query_def_string)

    return dataset.ModelQuery(query_type, name, query_string, parameters)


def _query_parameters_from_definition(query_string):
    """Extracts the parameters from the provided query definition string"""
    # Query parameters are one-indexed in SQLite
    current_position = 1
    parameters = []
    for param_name, input_param_type in _QUERY_PARAMETER_RE.findall(query_string):
        param_type = _field_type_get(input_param_type)
        parameter = dataset.ModelQueryParam(current_position, param_name, param_type)

        parameters.append(parameter)
        current_position += 1

    return parameters


def _query_def_remove_param_defs(query_def_string):
    """
    Removes the parameter definition strings from the query definition string and replaces
    them with the SQLite parameter placeholder value, a '?'
    """
    return _QUERY_PARAMETER_RE.sub('?', query_def_string)