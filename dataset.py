"""Defines classes to represent a cDAL dataset"""
from enum import Enum


class ModelFieldType(Enum):
    """Specifies the possible types for a model field"""
    PRIMARY_KEY = 'PrimaryKey'
    FOREIGN_KEY = 'ForeignKey'
    INTEGER = 'Integer'
    REAL = 'Real'
    TEXT = 'Text'
    BLOB = 'Blob'


class Dataset:
    """Represents a dataset to be stored in a single database"""

    def __init__(self, name, models):
        self.name = name
        self.models = models

    def __repr__(self):
        return 'Dataset(name={},models={})'.format(self.name, self.models)


class Model:
    """Represents a model corresponding to a single database table"""

    def __init__(self, name, fields, type_name=None, table_name=None):
        self.name = name
        self.fields = fields
        self._type_name = type_name
        self._table_name = table_name

    def __repr__(self):
        return 'Model(name={}, fields={})'.format(self.name, self.fields)

    def get_c_type(self):
        """Returns the name of the model's C struct type"""
        if self._type_name:
            c_type = self._type_name
        else:
            c_type = self.name

        return c_type

    def get_table_name(self):
        """Returns the name of the model's database table"""
        if self._table_name:
            table_name = self._table_name
        else:
            table_name = self.name

        return table_name


class ModelField:
    """Represents a field of a model corresponding to a single database table column"""

    def __init__(self, name, field_type, max_length=0):
        self.name = name
        self.field_type = field_type
        self.max_length = max_length

    def __repr__(self):
        return 'ModelField(name={},field_type={},max_length={})'.format(
            self.name, self.field_type, self.max_length)
