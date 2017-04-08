"""Contains functionality for parsing cDAL dataset definitions"""
import json
import jsonschema

import dataset


_SCHEMA_FILE_PATH = 'dataset.schema.json'


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
    fields = [_field_from_definition(field_definition) for field_definition in model_definition['fields']]

    # Get the values for the optional fields
    type_name = model_definition.get('typeName')
    table_name = model_definition.get('tableName')

    return dataset.Model(name, fields, type_name, table_name)


def _field_from_definition(field_definition):
    """Parses the model field from field definition dictionary"""
    name = field_definition['name']
    field_type = _field_type_get(field_definition['type'])
    max_length = _field_max_length_get(field_type, field_definition)

    return dataset.ModelField(name, field_type, max_length)


def _field_type_get(input_field_type):
    """Parses field type from field type specified in the definition"""
    matching_type = [field_type for field_type in dataset.ModelFieldType
                     if field_type.value == input_field_type]

    if len(matching_type) == 0:
        raise DatasetDefinitionError('Invalid field type: ' + input_field_type)

    return matching_type[0]


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