"""Manages rendering templates"""
from enum import Enum
from jinja2 import Environment, FileSystemLoader


_TEMPLATES_DIRECTORY = 'templates'


class CDALTemplate(Enum):
    C_TYPES_HEADER = 1
    C_TYPES_SOURCE = 2


def environment_create():
    """Creates an environment that can be used to render templates"""
    env = Environment(loader=FileSystemLoader(_TEMPLATES_DIRECTORY),
                      trim_blocks=True, lstrip_blocks=True)

    return env


def template_file_get(template):
    """Returns the path to the file for the specified template"""
    template_files = {
        CDALTemplate.C_TYPES_HEADER: 'ctypes.h',
        CDALTemplate.C_TYPES_SOURCE: 'ctypes.c',
    }
    template_file = template_files[template]

    return template_file


