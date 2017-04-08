"""Generates files to define and work with C structs corresponding to dataset models"""
import os
import codgen.templates as templates


def ctypes_header_file_create(dataset, output_dir, custom_includes=None):
    """Creates the C types header file in the specified output directory"""
    output_path = os.path.join(output_dir, _header_name_get(dataset))
    contents = ctypes_header_render(dataset, custom_includes)

    _file_write_all_data(output_path, contents)


def ctypes_header_render(dataset, custom_includes=None):
    """Renders the C types header for the provided dataset and returns the rendered string"""
    includes = {'<sqlite3.h>'}
    if custom_includes:
        includes = includes | custom_includes

    env = templates.environment_create()
    env.filters['header_guard_macro'] = _header_guard_macro_get
    env.filters['header_name'] = _header_name_get

    template_file = templates.template_file_get(templates.CDALTemplate.C_TYPES_HEADER)
    return env.get_template(template_file).render(dataset=dataset, includes=includes)


def ctypes_header_include_get(dataset):
    """Returns the string to include the C types header file"""
    return '"{}"'.format(_header_name_get(dataset))


def ctypes_source_file_create(dataset, output_dir, custom_includes=None):
    """Creates the C types source file in the specified output directory"""
    output_path = os.path.join(output_dir, _source_name_get(dataset))
    contents = ctypes_source_render(dataset, custom_includes)

    _file_write_all_data(output_path, contents)


def ctypes_source_render(dataset, custom_includes=None):
    """Renders the C types source file for the provided dataset and returns the rendered string"""
    includes = {'<stdlib.h>', '<string.h>', ctypes_header_include_get(dataset)}
    if custom_includes:
        includes = includes | custom_includes

    env = templates.environment_create()
    env.filters['source_name'] = _source_name_get

    template_file = templates.template_file_get(templates.CDALTemplate.C_TYPES_SOURCE)
    return env.get_template(template_file).render(dataset=dataset, includes=includes)


def _file_write_all_data(file_path, data):
    """Writes all data to the specified file path"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as output_file:
        output_file.write(data)


def _header_guard_macro_get(dataset):
    """Returns the name of the guard macro used to define the dataset's types header"""
    return '{}_CDAL_H'.format(dataset.name.upper())


def _header_name_get(dataset):
    """Returns the name for the C types header for the dataset"""
    return '{}.cdal.h'.format(dataset.name)


def _source_name_get(dataset):
    """Returns the name for the C types source file for the provided dataset"""
    return '{}.cdal.c'.format(dataset.name)