"""Generates code to access models stored in database tables"""
import os
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
    env.filters['get_all_function_name'] = _get_all_function_name
    env.filters['insert_new_function_name'] = _insert_new_function_name

    template_file = templates.template_file_get(templates.CDALTemplate.ACCESSOR_HEADER)
    return env.get_template(template_file).render(dataset=dataset, includes=includes)


def accessor_source_file_create(dataset, output_dir):
    """Generates and writes the dataset's accessor source C file to the output directory"""
    output_path = os.path.join(output_dir, _accessor_source_name_get(dataset))
    contents = accessor_source_render(dataset)

    templates.file_write_all_data(output_path, contents)


def accessor_source_render(dataset):
    """Renders the data accessor C source file for the dataset and returns the rendered string"""
    includes = [_accessor_header_include_get(dataset)]

    env = templates.environment_create()
    env.filters['source_name'] = _accessor_source_name_get
    env.filters['get_all_function_name'] = _get_all_function_name
    env.filters['insert_new_function_name'] = _insert_new_function_name
    env.filters['table_create_query_var'] = _table_create_query_var
    env.filters['field_column_enum'] = _field_column_enum

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


def _field_column_enum(field, model):
    """Returns the column enum value for the provided field"""
    return '{}_{}_COL'.format(model.get_table_name().upper(), field.name.upper())


def _get_all_function_name(model):
    """Returns the name of the function to retrieve all models from the database"""
    return '{}_get_all'.format(model.get_table_name())


def _insert_new_function_name(model):
    """Returns the name of the function to insert a new model object into the database"""
    return '{}_insert_new'.format(model.get_table_name())


def _table_create_query_var(model):
    """Returns the name of the variable to hold the model's table creation query"""
    return '{}_TABLE_CREATE'.format(model.get_table_name().upper())
