/************************************************************************
THIS FILE IS AUTO-GENERATED. DO NOT EDIT DIRECTLY. ALL CHANGES WILL BE LOST.

{{dataset | source_name}} - Contains functions for working with {{dataset.name}} dataset models.
************************************************************************/

/************************************************************************
                              INCLUDES
************************************************************************/

{% for include in includes %}
#include {{include}}
{% endfor %}

/************************************************************************
                               PROCEDURES
************************************************************************/

{% for model in dataset.models %}
/**************************************************
*
*    {{model.get_free_function_name()}} - Free {{model.name}}
*
*    Cleans up all resources owned by the provided {{model.name}}.
*
**************************************************/
void {{model.get_free_function_name()}}
    (
    {{model.get_pointer_type()}} model
    )
{
{% for field in model.fields if field.is_dynamically_allocated() %}
free( model->{{field.name}} );
{% endfor %}
{{model.get_init_function_name()}}( model );
} /* {{model.get_free_function_name()}} */


/**************************************************
*
*    {{model.get_init_function_name()}} - Initialize {{model.name}}
*
*    Initializes the provided {{model.name}}.
*
**************************************************/
void {{model.get_init_function_name()}}
    (
    {{model.get_pointer_type()}} model
    )
{
memset( model, 0, sizeof( *model ) );
} /* {{model.get_init_function_name()}} */


/**************************************************
*
*    {{model.get_list_free_function_name()}} - Free {{model.name}} list
*
*    Cleans up all resources owned by the provided list of {{model.name}} models.
*
**************************************************/
void {{model.get_list_free_function_name()}}
    (
    {{model.get_list_pointer_type()}} models
    )
{
{%if model.has_dynamic_fields() %}
int i;

for( i = 0; i < models->cnt; i++ )
   {
   {{model.get_free_function_name()}}( &models->list[i] );
   }

{% endif %}
free( models->list );

{{model.get_list_init_function_name()}}( models );
} /* {{model.get_list_free_function_name()}} */


/**************************************************
*
*    {{model.get_list_init_function_name()}} - Initialize {{model.name}} list
*
*    Initializes the provided list of {{model.name}} models.
*
**************************************************/
void {{model.get_list_init_function_name()}}
    (
    {{model.get_list_pointer_type()}} models
    )
{
memset( modesl, 0, sizeof( *models ) );
} /* {{model.get_list_init_function_name()}} */

{% endfor %}
