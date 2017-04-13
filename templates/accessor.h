/************************************************************************
THIS FILE IS AUTO-GENERATED. DO NOT EDIT DIRECTLY. ALL CHANGES WILL BE LOST.

{{dataset | header_name}}  - Declares functions for accessing {{dataset.name}} models.
************************************************************************/

#ifndef {{dataset | header_guard_macro}}
#define {{dataset | header_guard_macro}}

/************************************************************************
                              INCLUDES
************************************************************************/

{% for include in includes %}
#include {{include}}
{% endfor %}

/************************************************************************
                               PROCEDURES
************************************************************************/

int {{dataset | database_delete_all_data_function_name}}
    (
    sqlite3 * db
    );

int {{dataset | database_initialize_function_name}}
    (
    sqlite3 * db
    );

{% for model in dataset.models %}
int {{model | model_delete_by_id_function_name}}
    (
    sqlite3 * db,
    sqlite3_int64 id
    );

int {{model | model_find_by_id_function_name}}
    (
    sqlite3 * db,
    sqlite3_int64 id,
    int * found_out,
    {{model.get_pointer_type()}} model_out
    );

int {{model | model_insert_new_function_name}}
    (
    sqlite3 * db,
    {{model.get_pointer_type()}} model
    );

int {{model | model_save_existing_function_name}}
    (
    sqlite3 * db,
    {{model.get_constant_pointer_type()}} model
    );

int {{model | models_count_all_function_name}}
    (
    sqlite3 * db,
    int * count_out
    );

int {{model | models_delete_all_function_name}}
    (
    sqlite3 * db
    );

int {{model | models_get_all_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_pointer_type()}} models_out
    );

int {{model | models_insert_all_new_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_pointer_type()}} models
    );

int {{model | models_save_all_existing_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_constant_pointer_type()}} models
    );

{%for query in model.get_count_queries() %}
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}},
    {% endfor %}
    int * count_out
    );

{% endfor %}
{%for query in model.get_delete_queries() %}
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}}{%if not loop.last %},{% endif %}

    {% endfor %}
    );

{% endfor %}
{%for query in model.get_find_queries() %}
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}},
    {% endfor %}
    int * found_out,
    {{model.get_pointer_type()}} model_out
    );

{% endfor %}
{%for query in model.get_select_queries() %}
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}},
    {% endfor %}
    {{model.get_list_pointer_type()}} models_out
    );

{% endfor %}
{%for query in model.get_update_queries() %}
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}}{%if not loop.last %},{% endif %}

    {% endfor %}
    );

{% endfor %}
{% endfor %}

#endif /* #define {{dataset | header_guard_macro }}  */
