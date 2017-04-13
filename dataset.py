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

    def get_bind_function_name(self):
        """Returns the name of the function to bind values of the field's type to query parameters"""
        bind_functions = {
            ModelFieldType.PRIMARY_KEY: 'sqlite3_bind_int64',
            ModelFieldType.FOREIGN_KEY: 'sqlite3_bind_int64',
            ModelFieldType.INTEGER: 'sqlite3_bind_int',
            ModelFieldType.REAL: 'sqlite3_bind_double',
            ModelFieldType.TEXT: 'sqlite3_bind_text',
            ModelFieldType.BLOB: 'sqlite3_bind_blob'
        }

        return bind_functions[self]

    def get_c_type(self):
        """Returns the C type corresponding to the model field type"""
        c_types = {
            ModelFieldType.PRIMARY_KEY: 'sqlite3_int64',
            ModelFieldType.FOREIGN_KEY: 'sqlite3_int64',
            ModelFieldType.INTEGER: 'int',
            ModelFieldType.REAL: 'double',
            ModelFieldType.TEXT: 'char',
            ModelFieldType.BLOB: 'char',
        }

        return c_types[self]

    def get_column_type(self):
        """Returns the database column type corresponding to the field type"""
        column_types = {
            ModelFieldType.PRIMARY_KEY: 'INTEGER PRIMARY KEY',
            ModelFieldType.FOREIGN_KEY: 'INTEGER',
            ModelFieldType.INTEGER: 'INTEGER',
            ModelFieldType.REAL: 'REAL',
            ModelFieldType.TEXT: 'TEXT',
            ModelFieldType.BLOB: 'BLOB',
        }

        return column_types[self]

    def is_primitive_type(self):
        """Returns True if the field is a primitive type field"""
        primitive_types = {ModelFieldType.PRIMARY_KEY, ModelFieldType.FOREIGN_KEY,
                           ModelFieldType.INTEGER, ModelFieldType.REAL}

        return self in primitive_types


class ModelQueryType(Enum):
    """Specifies the type of a custom model query"""
    SELECT = 0
    FIND = 1
    COUNT = 2
    DELETE = 3
    UPDATE = 4


class Dataset:
    """Represents a dataset to be stored in a single database"""

    def __init__(self, name, models):
        self.name = name
        self.models = models

    def __repr__(self):
        return 'Dataset(name={},models={})'.format(self.name, self.models)


class Model:
    """Represents a model corresponding to a single database table"""

    def __init__(self, name, fields, queries, type_name=None, table_name=None):
        self.name = name
        self.fields = fields
        self.queries = queries
        self._type_name = type_name
        self._table_name = table_name

    def __repr__(self):
        return 'Model(name={}, fields={}, queries={})'.format(
            self.name, self.fields, self.queries)

    def get_c_type(self):
        """Returns the name of the model's C struct type"""
        if self._type_name:
            c_type = self._type_name
        else:
            c_type = self.name

        return c_type

    def get_constant_pointer_type(self):
        """Returns a string to declare a constant pointer to the model's C type"""
        return self.get_c_type() + ' const *'

    def get_count_queries(self):
        """Returns all count queries defined on the model"""
        return self._get_queries_by_type(ModelQueryType.COUNT)

    def get_delete_queries(self):
        """Returns all delete queries defined on the model"""
        return self._get_queries_by_type(ModelQueryType.DELETE)

    def get_find_queries(self):
        """Returns all find queries defined on the model"""
        return self._get_queries_by_type(ModelQueryType.FIND)

    def get_free_function_name(self):
        """Returns the name of the function to free model structs"""
        return self.name + '_free'

    def get_init_function_name(self):
        """Returns the name of the function to initialize model structs"""
        return self.name + '_init'

    def get_list_c_type(self):
        """Returns the name of the struct to hold a list of models"""
        return self.name + '_list_t'

    def get_list_constant_pointer_type(self):
        """Returns a string to declare a constant pointer to a list of models"""
        return self.get_list_c_type() + ' const *'

    def get_list_free_function_name(self):
        """Returns the name of the function to free a list of models"""
        return self.name + '_list_free'

    def get_list_init_function_name(self):
        """Returns the name of the function to initialize a list of models"""
        return self.name + '_list_init'

    def get_list_pointer_type(self):
        """Returns a string to declare a pointer to a list of models"""
        return self.get_list_c_type() + ' *'

    def get_pointer_type(self):
        """Returns a string to declare a pointer to the model's struct type"""
        return self.get_c_type() + ' *'

    def get_primary_key_field(self):
        """Returns the model's primary key field"""
        primary_key_field, = (field for field in self.fields if field.is_primary_key())
        return primary_key_field

    def get_select_queries(self):
        """Returns all select queries defined on the model"""
        return self._get_queries_by_type(ModelQueryType.SELECT)

    def get_table_name(self):
        """Returns the name of the model's database table"""
        if self._table_name:
            table_name = self._table_name
        else:
            table_name = self.name

        return table_name

    def get_update_queries(self):
        """Returns all update queries defined on the model"""
        return self._get_queries_by_type(ModelQueryType.UPDATE)

    def has_dynamic_fields(self):
        """Returns True if the model has any dynamically-allocated fields"""
        return any((field.is_dynamically_allocated() for field in self.fields))

    def _get_queries_by_type(self, query_type):
        """Returns all queries of the specified type"""
        return (query for query in self.queries if query.query_type == query_type)


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

    def get_read_result_function_name(self):
        """Returns the name of the function to read the field value from a query result"""
        primitive_result_functions = {
            ModelFieldType.PRIMARY_KEY: 'sqlite3_column_int64',
            ModelFieldType.FOREIGN_KEY: 'sqlite3_column_int64',
            ModelFieldType.INTEGER: 'sqlite3_column_int',
            ModelFieldType.REAL: 'sqlite3_column_double',
        }

        dynamic_result_functions = {
            ModelFieldType.TEXT: 'cqlite_dynamic_string_read',
            ModelFieldType.BLOB: 'cqlite_dynamic_blob_read',
        }

        fixed_size_result_functions = {
            ModelFieldType.TEXT: 'cqlite_fixed_length_string_read',
            ModelFieldType.BLOB: 'cqltie_fixed_length_blob_read',
        }

        if self.field_type.is_primitive_type():
            result_function = primitive_result_functions[self.field_type]
        elif self.is_dynamically_allocated():
            result_function = dynamic_result_functions[self.field_type]
        else:
            result_function = fixed_size_result_functions[self.field_type]

        return result_function

    def get_type_declaration(self):
        """Returns the string to declare the field's type"""
        c_type = self.field_type.get_c_type()

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
        return (not self.field_type.is_primitive_type()) and (not self.has_max_length())

    def is_primary_key(self):
        """Returns True if the field is a primary key field"""
        return self.field_type == ModelFieldType.PRIMARY_KEY


class ModelQuery:
    """Represents a custom user-defined query on a model database table"""

    def __init__(self, query_type, name, query_string, params):
        self.query_type = query_type
        self.name = name
        self.query_string = query_string
        self.params = list(params)

    def __repr__(self):
        return 'ModelQuery(query_type={},name={},query_string="{}",params={})'.format(
            self.query_type, self.name, self.query_string, self.params)


class ModelQueryParam:
    """Represents a parameter for a custom user-defined query on a model database table"""

    def __init__(self, position, name, param_type):
        self.position = position
        self.name = name
        self.param_type = param_type

    def __repr__(self):
        return 'ModelQueryParam(position={},name={},param_type={})'.format(
            self.position, self.name, self.param_type)

    def get_c_type(self):
        """Returns the C type of the query parameter"""
        pointer_types = {ModelFieldType.TEXT, ModelFieldType.BLOB}

        c_type = self.param_type.get_c_type()
        if self.param_type in pointer_types:
            c_type += ' *'

        return c_type
