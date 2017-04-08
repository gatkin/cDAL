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

    def get_free_function_name(self):
        """Returns the name of the function to free model structs"""
        return self.name + '_free'

    def get_init_function_name(self):
        """Returns the name of the function to initialize model structs"""
        return self.name + '_init'

    def get_list_c_type(self):
        """Returns the name of the struct to hold a list of models"""
        return self.name + '_list_t'

    def get_list_free_function_name(self):
        """Returns the name of the function to free a list of models"""
        return self.name + '_list_free'

    def get_list_init_function_name(self):
        """Returns the name of the function to initialize a list of models"""
        return self.name + '_list_init'

    def get_list_pointer_type(self):
        """Returns a string to declare a pointer to a list of models"""
        return self.get_list_c_type() + '*'

    def get_pointer_type(self):
        """Returns a string to declare a pointer to the model's struct type"""
        return self.get_c_type() + '*'

    def get_table_name(self):
        """Returns the name of the model's database table"""
        if self._table_name:
            table_name = self._table_name
        else:
            table_name = self.name

        return table_name

    def has_dynamic_fields(self):
        """Returns True if the model has any dynamically-allocated fields"""
        return any((field.is_dynamically_allocated() for field in self.fields))


class ModelField:
    """Represents a field of a model corresponding to a single database table column"""

    def __init__(self, name, field_type, max_length=0):
        self.name = name
        self.field_type = field_type
        self.max_length = max_length

    def __repr__(self):
        return 'ModelField(name={},field_type={},max_length={})'.format(
            self.name, self.field_type, self.max_length)

    def get_name_declaration(self):
        """Returns the string to declare the field's name"""
        if self.has_max_length():
            name_declaration = '{}[ {} ]'.format(self.name, self.max_length)
        else:
            name_declaration = self.name

        return name_declaration

    def get_type_declaration(self):
        """Returns the string to declare the field's type"""
        c_type = self._get_c_type()

        if self.is_dynamically_allocated():
            # Need to make it a pointer type if it is dynamically allocated
            type_declaration = c_type + '*'
        else:
            type_declaration = c_type

        return type_declaration

    def has_max_length(self):
        """Returns True if the model field has a specified maximum length"""
        return self.max_length > 0

    def is_dynamically_allocated(self):
        """Returns True if the memory for the field is dynamically allocated"""
        dynamic_types = {ModelFieldType.BLOB, ModelFieldType.TEXT}

        return (self.field_type in dynamic_types) and (not self.has_max_length())

    def _get_c_type(self):
        """Returns the C-type corresponding to the field's model field type"""
        c_types = {
            ModelFieldType.PRIMARY_KEY: 'sqlite3_int64',
            ModelFieldType.FOREIGN_KEY: 'sqlite3_int64',
            ModelFieldType.INTEGER: 'int',
            ModelFieldType.REAL: 'double',
            ModelFieldType.TEXT: 'char',
            ModelFieldType.BLOB: 'char',
        }

        return c_types[self.field_type]
