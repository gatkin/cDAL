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

int {{dataset | database_initialize_function_name}}
    (
    sqlite3 * db
    );

{% for model in dataset.models %}
int {{model | models_get_all_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_pointer_type()}} models_out
    );

int {{model | model_insert_new_function_name}}
    (
    sqlite3 * db,
    {{model.get_pointer_type()}} model
    );

{% endfor %}

#endif /* #define {{dataset | header_guard_macro }}  */
