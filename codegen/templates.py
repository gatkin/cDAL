"""Manages rendering templates"""
import os
from enum import Enum
from jinja2 import Environment, FileSystemLoader


_TEMPLATES_DIRECTORY = 'templates'


class CDALTemplate(Enum):
    C_TYPES_HEADER = 1
    C_TYPES_SOURCE = 2
    ACCESSOR_HEADER = 3
    ACCESSOR_SOURCE = 4


def environment_create():
    """Creates an environment that can be used to render templates"""
    env = Environment(loader=FileSystemLoader(_TEMPLATES_DIRECTORY),
                      trim_blocks=True, lstrip_blocks=True)

    return env


def file_write_all_data(file_path, data):
    """Writes all data to the specified file path"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as output_file:
        output_file.write(data)


def template_file_get(template):
    """Returns the path to the file for the specified template"""
    template_files = {
        CDALTemplate.C_TYPES_HEADER: 'ctypes.h',
        CDALTemplate.C_TYPES_SOURCE: 'ctypes.c',
        CDALTemplate.ACCESSOR_HEADER: 'accessor.h',
        CDALTemplate.ACCESSOR_SOURCE: 'accessor.c',
    }
    template_file = template_files[template]

    return template_file


