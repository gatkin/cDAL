"""Generates code to access models stored in database tables"""
import os

from codegen import templates
from codegen.ctypes import ctypes_header_include_get
from dataset import ModelQueryType


def accessor_header_file_create(dataset, output_dir):
    """Generates and writes the dataset's accessor header file to the output directory"""
    output_path = os.path.join(output_dir, _accessor_header_name_get(dataset))
    contents = accessor_header_render(dataset)

    templates.file_write_all_data(output_path, contents)


def accessor_header_render(dataset):
    """Renders the data accessor header for the dataset and returns the rendered string"""
    includes = ['<sqlite3.h>', ctypes_header_include_get(dataset)]

    env = templates.environment_create()
    env.filters['database_delete_all_data_function_name'] = _database_delete_all_data_function_name
    env.filters['database_initialize_function_name'] = _database_initialize_function_name
    env.filters['header_guard_macro'] = _accessor_header_guard_macro_get
    env.filters['header_name'] = _accessor_header_name_get
    env.filters['model_delete_by_id_function_name'] = _model_delete_by_id_function_name
    env.filters['model_find_by_id_function_name'] = _model_find_by_id_function_name
    env.filters['model_insert_new_function_name'] = _model_insert_new_function_name
    env.filters['model_save_existing_function_name'] = _model_save_existing_function_name
    env.filters['models_get_all_function_name'] = _models_get_all_function_name
    env.filters['models_count_all_function_name'] = _models_count_all_function_name
    env.filters['models_delete_all_function_name'] = _models_delete_all_function_name
    env.filters['models_insert_all_new_function_name'] = _models_insert_all_new_function_name
    env.filters['models_save_all_existing_function_name'] = _models_save_all_function_name

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
    env.filters['database_delete_all_data_function_name'] = _database_delete_all_data_function_name
    env.filters['database_initialize_function_name'] = _database_initialize_function_name
    env.filters['field_bind_function_call'] = _field_bind_function_call
    env.filters['field_column_enum'] = _field_column_enum
    env.filters['field_read_result_function_call'] = _field_read_result_function_call
    env.filters['model_add_to_result_list_function_name'] = _model_add_to_result_list_function_name
    env.filters['model_delete_by_id_function_name'] = _model_delete_by_id_function_name
    env.filters['model_find_by_id_function_name'] = _model_find_by_id_function_name
    env.filters['model_from_row_result_function_name'] = _model_from_row_result_function_name
    env.filters['model_insert_new_function_name'] = _model_insert_new_function_name
    env.filters['model_insert_query_string'] = _model_insert_query_string
    env.filters['model_save_existing_function_name'] = _model_save_existing_function_name
    env.filters['models_count_all_function_name'] = _models_count_all_function_name
    env.filters['models_delete_all_function_name'] = _models_delete_all_function_name
    env.filters['models_get_all_function_name'] = _models_get_all_function_name
    env.filters['models_insert_all_new_function_name'] = _models_insert_all_new_function_name
    env.filters['models_save_all_existing_function_name'] = _models_save_all_function_name
    env.filters['query_get_full_string'] = _query_get_full_string
    env.filters['query_param_bind_call'] = _query_param_bind_call
    env.filters['select_query_get_count_query_string'] = _select_query_get_count_query_string
    env.filters['source_name'] = _accessor_source_name_get
    env.filters['table_create_query_var'] = _table_create_query_var

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


def _database_delete_all_data_function_name(dataset):
    """Returns the name of the function to delete all data from the dataset's database"""
    return '{}_database_delete_all_data'.format(dataset.name)


def _database_initialize_function_name(dataset):
    """Returns the name of the function to initialize the dataset's database"""
    return '{}_database_initialize'.format(dataset.name)


def _field_bind_function_call(field, model, query_var, model_var):
    """Returns the function call to bind the model field's value to a query variable"""
    # SQLite query parameters are 1-indexed, so we need to add one the the column
    # enum value which is 0-index.
    if field.field_type.is_primitive_type():
        bind_call_template ='{bind_function}( {query_var}, ({column_enum} + 1), {model_var}->{field_name} )'
    else:
        bind_call_template ='{bind_function}( {query_var}, ({column_enum} + 1), {model_var}->{field_name}, -1, SQLITE_TRANSIENT )'

    bind_call = bind_call_template.format(bind_function=field.field_type.get_bind_function_name(),
                                          query_var=query_var, column_enum=_field_column_enum(field, model),
                                          model_var=model_var, field_name=field.name)
    return bind_call


def _field_column_enum(field, model):
    """Returns the column enum value for the provided field"""
    return '{}_{}_COL'.format(model.get_table_name().upper(), field.name.upper())


def _field_read_result_function_call(field, model, query_var, model_var, success_var):
    """Returns the function call to read a model field value from a query result"""
    if field.field_type.is_primitive_type():
        result_call_template ='{model_var}->{field_name} = {result_function}( {query_var}, {column_enum} );'
    elif field.is_dynamically_allocated():
        result_call_template = '{success_var} &= ( CQLITE_SUCCESS == {result_function}( {query_var}, {column_enum}, &{model_var}->{field_name} ) );'
    else:
        # Fixed-size field
        result_call_template = '{success_var} &= ( CQLITE_SUCCESS == {result_function}( {query_var}, {column_enum}, {model_var}->{field_name}, sizeof( {model_var}->{field_name} ) ) );'

    result_call = result_call_template.format(result_function=field.get_read_result_function_name(),
                                              success_var=success_var, model_var=model_var, query_var=query_var,
                                              column_enum=_field_column_enum(field, model), field_name=field.name)

    return result_call


def _model_add_to_result_list_function_name(model):
    """Returns the name of the function to add a model to a query result list"""
    return '{}_add_to_result_list'.format(model.name)


def _model_delete_by_id_function_name(model):
    """Returns the name of the function to delete a model by id"""
    return '{}_delete_by_id'.format(model.get_table_name())


def _model_find_by_id_function_name(model):
    """Returns the name of the function to find a model record by its id"""
    return '{}_find_by_id'.format(model.get_table_name())


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


def _model_save_existing_function_name(model):
    """Returns the name of the function to save an existing model record into the database"""
    return '{}_save_existing'.format(model.get_table_name())


def _models_count_all_function_name(model):
    """Returns the name of the function get the number of models in the database"""
    return '{}_count_all'.format(model.get_table_name())


def _models_delete_all_function_name(model):
    """Returns the name of the function to delete all models from the database"""
    return '{}_delete_all'.format(model.get_table_name())


def _models_get_all_function_name(model):
    """Returns the name of the function to retrieve all models from the database"""
    return '{}_get_all'.format(model.get_table_name())


def _models_insert_all_new_function_name(model):
    """Returns the name of the function to insert a list of models as new records"""
    return '{}_insert_all_new'.format(model.get_table_name())


def _models_save_all_function_name(model):
    """Returns the name of the function to save a list of models as existing records"""
    return '{}_save_all_existing'.format(model.get_table_name())


def _query_get_full_string(query, model):
    """Returns the full string for the query that can be executed on the database"""
    query_templates = {
        ModelQueryType.COUNT: 'SELECT COUNT(*) FROM {table_name} {query_string}',
        ModelQueryType.FIND: 'SELECT * FROM {table_name} {query_string} LIMIT 1',
        ModelQueryType.DELETE: 'DELETE FROM {table_name} {query_string}',
        ModelQueryType.SELECT: 'SELECT * FROM {table_name} {query_string}',
        ModelQueryType.UPDATE: 'UPDATE {table_name} {query_string}'
    }
    query_template = query_templates[query.query_type]

    full_query_string = query_template.format(table_name=model.get_table_name(), query_string=query.query_string)
    return '"' + full_query_string + '"'


def _query_param_bind_call(query_param, query_var):
    """Returns the function call to bind a parameter to a custom query"""
    if query_param.param_type.is_primitive_type():
        bind_call_template ='{bind_function}( {query_var}, {param_position}, {param_name} )'
    else:
        bind_call_template ='{bind_function}( {query_var}, {param_position}, {param_name}, -1, SQLITE_TRANSIENT )'

    bind_call = bind_call_template.format(bind_function=query_param.param_type.get_bind_function_name(),
                                          query_var=query_var, param_position=query_param.position,
                                          param_name=query_param.name)
    return bind_call


def _select_query_get_count_query_string(query, model):
    """Returns the count query string that returns the number of results that will be read by a select query"""
    count_query = 'SELECT COUNT(*) FROM {table_name} {query_string}'.format(
        table_name=model.get_table_name(), query_string=query.query_string)
    
    return '"' + count_query + '"'


def _table_create_query_var(model):
    """Returns the name of the variable to hold the model's table creation query"""
    return '{}_TABLE_CREATE'.format(model.get_table_name().upper())
