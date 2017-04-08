"""Generates files to define and work with C structs corresponding to dataset models"""
import codgen.templates as templates


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


def _header_guard_macro_get(dataset):
    """Returns the name of the guard macro used to define the dataset's types header"""
    return '{}_CDAL_H'.format(dataset.name.upper())


def _header_name_get(dataset):
    """Returns the name for the C types header for the dataset with the specified name"""
    return '{}.cdal.h'.format(dataset.name)
