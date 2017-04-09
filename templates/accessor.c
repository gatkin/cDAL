/************************************************************************
THIS FILE IS AUTO-GENERATED. DO NOT EDIT DIRECTLY. ALL CHANGES WILL BE LOST.

{{dataset | source_name}} - Contains functions for accessing {{dataset.name}} models.
************************************************************************/

/************************************************************************
                              INCLUDES
************************************************************************/

{% for include in includes %}
#include {{include}}
{% endfor %}

/************************************************************************
                            MEMORY CONSTANTS
************************************************************************/
{% for model in dataset.models %}
static char const * const {{model | table_create_query_var}} =
    "CREATE TABLE IF NOT EXISTS {{model.get_table_name()}}"
    "("
    {% for field in model.fields %}
    "{{field.name}} {{field.get_column_type()}}{% if not loop.last %},{% endif %}"
    {% endfor %}
    ");";

enum
    {
    {% for field in model.fields %}
    {{field | field_column_enum(model)}},
    {% endfor %}
    };

{% endfor %}

/************************************************************************
                               PROCEDURES
************************************************************************/

{% for model in dataset.models %}
/**************************************************
*
*    {{model | get_all_function_name}} - Get all {{model.name}} models
*
*    Retrieves all {{model.name}} models from the
*    provided database. The caller must call
*    {{model.get_list_free_function_name()}} on models_out.
*
**************************************************/
int {{model | get_all_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_pointer_type()}} models_out
    )
{
return 0;
}


/**************************************************
*
*    {{model | insert_new_function_name}} - Insert new {{model.name}}
*
*    Inserts a new {{model.name}} record into the
*    provided database. The model parameter's id field
*    is modified with the generated insert id.
*
**************************************************/
int {{model | insert_new_function_name}}
    (
    sqlite3 * db,
    {{model.get_pointer_type()}} model
    )
{
return 0;
}

{% endfor %}