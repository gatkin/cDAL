/************************************************************************
THIS FILE IS AUTO-GENERATED. DO NOT EDIT DIRECTLY. ALL CHANGES WILL BE LOST.

{{dataset | header_name}}  - Defines types for the {{dataset.name}} dataset.
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
                               TYPES
************************************************************************/

{% for model in dataset.models %}
typedef struct
    {
    {% for field in model.fields %}
    {{field.get_type_declaration()}} {{field.get_name_declaration()}};
    {% endfor %}
    } {{model.get_c_type()}};

typedef struct
    {
    {{model.get_pointer_type()}} list;
    int cnt;
    } {{model.get_list_c_type()}};

{% endfor %}

/************************************************************************
                               PROCEDURES
************************************************************************/

{% for model in dataset.models %}
void {{model.get_free_function_name()}}
    (
    {{model.get_pointer_type()}} model
    );

void {{model.get_init_function_name()}}
    (
    {{model.get_pointer_type()}} model
    );

void {{model.get_list_free_function_name()}}
    (
    {{model.get_list_pointer_type()}} models
    );

void {{model.get_list_init_function_name()}}
    (
    {{model.get_list_pointer_type()}} models
    );

{% endfor %}

#endif /* #define {{dataset | header_guard_macro }}  */
