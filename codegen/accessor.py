"""Generates code to access models stored in database tables"""
import os
from string import Template
from codegen import templates
from codegen.ctypes import ctypes_header_include_get


def accessor_header_file_create(dataset, output_dir):
    """Generates and writes the dataset's accessor header file to the output directory"""
    output_path = os.path.join(output_dir, _accessor_header_name_get(dataset))
    contents = accessor_header_render(dataset)

    templates.file_write_all_data(output_path, contents)


def accessor_header_render(dataset):
    """Renders the data accessor header for the dataset and returns the rendered string"""
    includes = ['<sqlite3.h>', ctypes_header_include_get(dataset)]

    env = templates.environment_create()
    env.filters['header_guard_macro'] = _accessor_header_guard_macro_get
    env.filters['header_name'] = _accessor_header_name_get
    env.filters['models_get_all_function_name'] = _models_get_all_function_name
    env.filters['model_insert_new_function_name'] = _model_insert_new_function_name
    env.filters['database_initialize_function_name'] = _database_initialize_function_name

    template_file = templates.template_file_get(templates.CDALTemplate.ACCESSOR_HEADER)
    return env.get_template(template_file).render(dataset=dataset, includes=includes)


def accessor_source_file_create(dataset, output_dir):
    """Generates and writes the dataset's accessor source C file to the output directory"""
    output_path = os.path.join(output_dir, _accessor_source_name_get(dataset))
    contents = accessor_source_render(dataset)

    templates.file_write_all_data(output_path, contents)


def accessor_source_render(dataset):
    """Renders the data accessor C source file for the dataset and returns the rendered string"""
    includes = ['<stddef.h>', '"cqlite.h"', _accessor_header_include_get(dataset)]

    env = templates.environment_create()
    env.filters['source_name'] = _accessor_source_name_get
    env.filters['models_get_all_function_name'] = _models_get_all_function_name
    env.filters['model_insert_new_function_name'] = _model_insert_new_function_name
    env.filters['table_create_query_var'] = _table_create_query_var
    env.filters['field_column_enum'] = _field_column_enum
    env.filters['model_from_row_result_function_name'] = _model_from_row_result_function_name
    env.filters['model_add_to_result_list_function_name'] = _model_add_to_result_list_function_name
    env.filters['model_insert_query_string'] = _model_insert_query_string
    env.filters['field_bind_function_call'] = _field_bind_function_call
    env.filters['database_initialize_function_name'] = _database_initialize_function_name
    env.filters['field_read_result_function_call'] = _field_read_result_function_call

    template_file = templates.template_file_get(templates.CDALTemplate.ACCESSOR_SOURCE)
    return env.get_template(template_file).render(dataset=dataset, includes=includes)


def _accessor_header_guard_macro_get(dataset):
    """Returns the guard macro for the dataset's accessor header file"""
    return '{}_CDAL_ACCESSOR_H'.format(dataset.name.upper())


def _accessor_header_include_get(dataset):
    """Returns the string to include the accessor header file"""
    return '"{}"'.format(_accessor_header_name_get(dataset))


def _accessor_header_name_get(dataset):
    """Returns the name of the dataset's accessor header file"""
    return '{}.cdal.accessor.h'.format(dataset.name)


def _accessor_source_name_get(dataset):
    """Returns the name of the dataset's accessor source file"""
    return '{}.cdal.accessor.c'.format(dataset.name)


def _database_initialize_function_name(dataset):
    """Returns the name of the function to initialize the dataset's database"""
    return '{}_database_initialize'.format(dataset.name)


def _field_bind_function_call(field, model, query_var, model_var):
    """Returns the function call to bind the model field's value to a query variable"""
    # SQLite query parameters are 1-indexed, so we need to add one the the column
    # enum value which is 0-index.
    if field.is_primitive_type():
        bind_call_template = Template(
            '$bind_function( $query_var, ($column_enum + 1), $model_var->$field_name )'
        )
    else:
        bind_call_template = Template(
            '$bind_function( $query_var, ($column_enum + 1), $model_var->$field_name, -1, SQLITE_TRANSIENT )'
        )

    bind_call = bind_call_template.substitute(bind_function=field.get_bind_function_name(),
                                              query_var=query_var, column_enum=_field_column_enum(field, model),
                                              model_var=model_var, field_name=field.name)

    return bind_call


def _field_column_enum(field, model):
    """Returns the column enum value for the provided field"""
    return '{}_{}_COL'.format(model.get_table_name().upper(), field.name.upper())


def _field_read_result_function_call(field, model, query_var, model_var, success_var):
    """Returns the function call to read a model field value from a query result"""
    if field.is_primitive_type():
        result_call_template = Template(
            '$model_var->$field_name = $result_function( $query_var, $column_enum );'
        )
    elif field.is_dynamically_allocated():
        result_call_template = Template(
            '$success_var &= ( CQLITE_SUCCESS == $result_function( $query_var, $column_enum, &$model_var->$field_name ) );'
        )
    else:
        result_call_template = Template(
            '$success_var &= ( CQLITE_SUCCESS == $result_function( $query_var, $column_enum, $model_var->$field_name, sizeof( $model_var->$field_name ) ) );'
        )

    result_call = result_call_template.substitute(result_function=field.get_read_result_function_name(),
                                                  success_var=success_var, model_var=model_var, query_var=query_var,
                                                  column_enum=_field_column_enum(field, model), field_name=field.name)

    return result_call


def _model_add_to_result_list_function_name(model):
    """Returns the name of the function to add a model to a query result list"""
    return '{}_add_to_result_list'.format(model.name)


def _model_from_row_result_function_name(model):
    """Returns the name of the function to read a model from a query result"""
    return '{}_from_row_result'.format(model.name)


def _model_insert_new_function_name(model):
    """Returns the name of the function to insert a new model object into the database"""
    return '{}_insert_new'.format(model.get_table_name())


def _model_insert_query_string(model):
    """Returns the query string to insert a model into the database"""
    parameters = ', '.join(['?'] * len(model.fields))
    query = '"INSERT OR REPLACE INTO {} VALUES ({});"'.format(
        model.get_table_name(), parameters)

    return query


def _models_get_all_function_name(model):
    """Returns the name of the function to retrieve all models from the database"""
    return '{}_get_all'.format(model.get_table_name())


def _table_create_query_var(model):
    """Returns the name of the variable to hold the model's table creation query"""
    return '{}_TABLE_CREATE'.format(model.get_table_name().upper())
