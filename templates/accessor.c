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
    "{{field.name}} {{field.field_type.get_column_type()}}{% if not loop.last %},{% endif %}"
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
static int {{model | model_add_to_result_list_function_name}}
    (
    sqlite3_stmt * query,
    void * model_list,
    int next_model_list_idx
    );

static int {{model | model_from_row_result_function_name}}
    (
    sqlite3_stmt * query,
    void * model_out
    );

{% endfor %}

/**************************************************
*
*    {{dataset | database_delete_all_data_function_name}} - Delete all data
*
*    Deletes all data in the {{dataset.name}} database.
*
**************************************************/
int {{dataset | database_delete_all_data_function_name}}
    (
    sqlite3 * db
    )
{
int success;

success = 1;

{%for model in dataset.models %}
success &= ( SQLITE_OK == sqlite3_exec( db, "DELETE FROM {{model.get_table_name()}};", NULL, NULL, NULL ) );
{% endfor %}

return success;
}


/**************************************************
*
*    {{dataset | database_initialize_function_name}} - Initialize database
*
*    Initializes all tables in the {{dataset.name}}
*    database.
*
**************************************************/
int {{dataset | database_initialize_function_name}}
    (
    sqlite3 * db
    )
{
int success;

success = 1;

{% for model in dataset.models %}
success &= ( SQLITE_OK == sqlite3_exec( db, {{model | table_create_query_var}}, NULL, NULL, NULL ) );
{% endfor %}

return success;
}


{% for model in dataset.models %}
/**************************************************
*
*    {{model | model_delete_by_id_function_name}} - Delete {{model.name}} by id
*
*    Inserts the {{model.name}} record in the database
*    with the specified id.
*
**************************************************/
int {{model | model_delete_by_id_function_name}}
    (
    sqlite3 * db,
    sqlite3_int64 id
    )
{
int success;
sqlite3_stmt * delete_query;

delete_query = NULL;

success = ( SQLITE_OK == sqlite3_prepare_v2( db, "DELETE FROM {{model.get_table_name()}} WHERE {{model.get_primary_key_field().name}} = ?;", -1, &delete_query, NULL ) );
success &= ( SQLITE_OK == sqlite3_bind_int64( delete_query, 1, id ) );

success &= ( SQLITE_DONE == sqlite3_step( delete_query ) );

sqlite3_finalize( delete_query );

return success;
}


/**************************************************
*
*    {{model | model_find_by_id_function_name}} - Find {{model.name}} by id
*
*    Retrieves the model in the {{model.get_table_name()}} database table
*    with the specified id. If a model is found, then
*    found_out will be set to 1, and model_out will
*    be populated with the retrieved record. Otherwise,
*    found_out will be set ot 0. It is the caller's
*    responsibility to call {{model.get_free_function_name()}} on model_out.
*
**************************************************/
int {{model | model_find_by_id_function_name}}
    (
    sqlite3 * db,
    sqlite3_int64 id,
    int * found_out,
    {{model.get_pointer_type()}} model_out
    )
{
cqlite_rcode_t rcode;

*found_out = 0;
{{model.get_init_function_name()}}( model_out );

rcode = cqlite_find_by_id
    (
    db,
    "SELECT * FROM {{model.get_table_name()}} WHERE {{model.get_primary_key_field().name}} = ?;",
    id,
    {{model | model_from_row_result_function_name}},
    found_out,
    model_out
    );

return ( CQLITE_SUCCESS == rcode );
}


/**************************************************
*
*    {{model | model_insert_new_function_name}} - Insert new {{model.name}}
*
*    Inserts a new {{model.name}} record into the
*    provided database. The model parameter's id field
*    is modified with the generated insert id.
*
**************************************************/
int {{model | model_insert_new_function_name}}
    (
    sqlite3 * db,
    {{model.get_pointer_type()}} model
    )
{
int success;
sqlite3_stmt * insert_query;

insert_query = NULL;

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{ model | model_insert_query_string}}, -1, &insert_query, NULL ) );

// Bind all but the model's primary key so a new primary key is generated upon insertion
{%for field in model.fields if not field.is_primary_key() %}
success &= ( SQLITE_OK == {{field | field_bind_function_call(model, 'insert_query', 'model')}} );
{% endfor %}

success &= ( CQLITE_SUCCESS == cqlite_insert_query_execute( db, insert_query, &model->{{model.get_primary_key_field().name}} ) );

sqlite3_finalize( insert_query );

return success;
}


/**************************************************
*
*    {{model | model_save_existing_function_name}} - Save existing {{model.name}}
*
*    Saves the provided {{model.name}} as an existing
*    record in the database, updating any records
*    with a matching primary key.
*
**************************************************/
int {{model | model_save_existing_function_name}}
    (
    sqlite3 * db,
    {{model.get_constant_pointer_type()}} model
    )
{
int success;
sqlite3_stmt * insert_query;

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{ model | model_insert_query_string}}, -1, &insert_query, NULL ) );

{%for field in model.fields%}
success &= ( SQLITE_OK == {{field | field_bind_function_call(model, 'insert_query', 'model')}} );
{% endfor %}

success &= ( SQLITE_DONE == sqlite3_step( insert_query ) );

sqlite3_finalize( insert_query );

return success;
}


/**************************************************
*
*    {{model | models_count_all_function_name}} - Get number of {{model.name}} models
*
*    Gets the number of {{model.name}} models in
*    the database.
*
**************************************************/
int {{model | models_count_all_function_name}}
    (
    sqlite3 * db,
    int * count_out
    )
{
cqlite_rcode_t rcode;

rcode = cqlite_count_query_execute( db, "SELECT COUNT(*) FROM {{model.get_table_name()}};", count_out );

return ( CQLITE_SUCCESS == rcode );
}


/**************************************************
*
*    {{model | models_get_all_function_name}} - Get all {{model.name}} models
*
*    Retrieves all {{model.name}} models from the
*    provided database. The caller must call
*    {{model.get_list_free_function_name()}} on models_out.
*
**************************************************/
int {{model | models_get_all_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_pointer_type()}} models_out
    )
{
cqlite_rcode_t rcode;

{{model.get_list_init_function_name()}}( models_out );

rcode = cqlite_select_query_execute
    (
    db,
    "SELECT * FROM {{model.get_table_name()}};",
    "SELECT COUNT(*) FROM {{model.get_table_name()}};",
    {{model | model_add_to_result_list_function_name}},
    sizeof( *models_out->list ),
    (void**)&models_out->list,
    &models_out->cnt
    );

return ( CQLITE_SUCCESS == rcode );
}


/**************************************************
*
*    {{model | models_insert_all_new_function_name}} - Insert all {{model.name}} as new models
*
*    Inserts all provided {{model.name}} models into the
*    database. The id fields of each item in the models
*    list is modified with the generated insert id for
*    that model.
*
**************************************************/
int {{model | models_insert_all_new_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_pointer_type()}} models
    )
{
int success;
sqlite3_stmt * insert_query;
int i;
{{model.get_pointer_type()}} model;

insert_query = NULL;

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{ model | model_insert_query_string}}, -1, &insert_query, NULL ) );

for( i = 0; ( success ) && ( i < models->cnt ); i++)
    {
    model = &models->list[i];

    // Bind all but the model's primary key so a new primary key is generated upon insertion
    {%for field in model.fields if not field.is_primary_key() %}
    success &= ( SQLITE_OK == {{field | field_bind_function_call(model, 'insert_query', 'model')}} );
    {% endfor %}

    success &= ( CQLITE_SUCCESS == cqlite_insert_query_execute( db, insert_query, &model->{{model.get_primary_key_field().name}} ) );

    success &= ( SQLITE_OK == sqlite3_clear_bindings( insert_query ) );
    }

sqlite3_finalize( insert_query );

return success;
}


/**************************************************
*
*    {{model | models_save_all_existing_function_name}} - Save all {{model.name}} as existing models
*
*    Saves all provided {{model.name}} models into the
*    database as existing records updating any previous
*    records with matching ids.
*
**************************************************/
int {{model | models_save_all_existing_function_name}}
    (
    sqlite3 * db,
    {{model.get_list_constant_pointer_type()}} models
    )
{
int success;
sqlite3_stmt * insert_query;
int i;
{{model.get_pointer_type()}} model;

insert_query = NULL;

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{ model | model_insert_query_string}}, -1, &insert_query, NULL ) );

for( i = 0; ( success ) && ( i < models->cnt ); i++)
    {
    model = &models->list[i];

    {%for field in model.fields %}
    success &= ( SQLITE_OK == {{field | field_bind_function_call(model, 'insert_query', 'model')}} );
    {% endfor %}

    success &= ( SQLITE_DONE == sqlite3_step( insert_query ) );

    success &= ( SQLITE_OK == sqlite3_clear_bindings( insert_query ) );
    }

sqlite3_finalize( insert_query );

return success;
}


{%for query in model.get_count_queries() %}
/**************************************************
*
*    {{query.name}}
*
*    Executes a custom count query with the provided
*    parameters on the {{model.get_table_name()}} database table
*    and outputs the retrieved count.
*
**************************************************/
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}},
    {% endfor %}
    int * count_out
    )
{
int success;
sqlite3_stmt * count_query;

count_query = NULL;
*count_out = 0;

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{query | query_get_full_string(model)}}, -1, &count_query, NULL ) );

{%for query_param in query.params %}
success &= ( SQLITE_OK == {{query_param | query_param_bind_call('count_query')}} );
{% endfor %}

success &= ( CQLITE_SUCCESS == cqlite_count_query_execute_prepared( count_query, count_out ) );

sqlite3_finalize( count_query );

return success;
}


{% endfor %}
{%for query in model.get_delete_queries() %}
/**************************************************
*
*    {{query.name}}
*
*    Executes a custom delete query with the provided
*    parameters on the {{model.get_table_name()}} database table.
*
**************************************************/
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}}{%if not loop.last %},{% endif %}

    {% endfor %}
    )
{
int success;
sqlite3_stmt * delete_query;

delete_query = NULL;

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{query | query_get_full_string(model)}}, -1, &delete_query, NULL ) );

{%for query_param in query.params %}
success &= ( SQLITE_OK == {{query_param | query_param_bind_call('delete_query')}} );
{% endfor %}

success &= ( SQLITE_DONE == sqlite3_step( delete_query ) );

sqlite3_finalize( delete_query );

return success;
}


{% endfor %}
{%for query in model.get_find_queries() %}
/**************************************************
*
*    {{query.name}}
*
*    Executes a custom find query that is expected to
*    only return a single result with the provided
*    parameters on the {{model.get_table_name()}} database table.
*    If a record was found, found_out will be set
*    to 1, and model_out will be populated with the
*    matching record. Otherwise, found_out will be
*    set to 0. It is the caller's responsibility
*    to call {{model.get_free_function_name()}} on model_out.
*
**************************************************/
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}},
    {% endfor %}
    int * found_out,
    {{model.get_pointer_type()}} model_out
    )
{
int success;
sqlite3_stmt * find_query;

find_query = NULL;
*found_out = 0;
{{model.get_init_function_name()}}( model_out );

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{query | query_get_full_string(model)}}, -1, &find_query, NULL ) );

{%for query_param in query.params %}
success &= ( SQLITE_OK == {{query_param | query_param_bind_call('find_query')}} );
{% endfor %}

success &= ( CQLITE_SUCCESS == cqlite_find( find_query, {{model | model_from_row_result_function_name}}, found_out, model_out ) );

sqlite3_finalize( find_query );

return success;
}    


{% endfor %}
{%for query in model.get_select_queries() %}
/**************************************************
*
*    {{query.name}}
*
*    Executes a custom select query that is expected to
*    return possibly many result with the provided
*    parameters on the {{model.get_table_name()}} database table.
*    The caller must call {{model.get_list_free_function_name()}}
*    on models_out.
*
**************************************************/
int {{query.name}}
    (
    sqlite3 * db,
    {%for query_param in query.params %}
    {{query_param.get_c_type()}} {{query_param.name}},
    {% endfor %}
    {{model.get_list_pointer_type()}} models_out
    )
{
int success;
sqlite3_stmt * select_query;
sqlite3_stmt * count_query;
cqlite_rcode_t cqlite_rcode;

select_query = NULL;
count_query = NULL;
{{model.get_list_init_function_name()}}( models_out );

success = ( SQLITE_OK == sqlite3_prepare_v2( db, {{query | query_get_full_string(model)}}, -1, &select_query, NULL ) ) &&
          ( SQLITE_OK == sqlite3_prepare_v2( db, {{query | select_query_get_count_query_string(model)}}, -1, &count_query, NULL ) );

{%for query_param in query.params %}
success &= ( SQLITE_OK == {{query_param | query_param_bind_call('select_query')}} );
{% endfor %}

{%for query_param in query.params %}
success &= ( SQLITE_OK == {{query_param | query_param_bind_call('count_query')}} );
{% endfor %}

if( success )
   {
    cqlite_rcode = cqlite_select_query_execute_prepared
        (
        select_query,
        count_query,
        {{model | model_add_to_result_list_function_name}},
        sizeof( *models_out->list ),
        (void**)&models_out->list,
        &models_out->cnt
        );
    success = ( CQLITE_SUCCESS == cqlite_rcode );
   }

sqlite3_finalize( select_query );
sqlite3_finalize( count_query );

return success;
}


{% endfor %}
{% endfor %}

{% for model in dataset.models %}
/**************************************************
*
*    {{model | model_add_to_result_list_function_name}} - Add to result list
*
*    A cqlite_model_add_to_list_func_t function to
*    read the provided query row result as a {{model.name}}
*    model into the provided list at the specified index.
*
**************************************************/
static int {{model | model_add_to_result_list_function_name}}
    (
    sqlite3_stmt * query,
    void * model_list,
    int next_model_list_idx
    )
{
{{model.get_pointer_type()}} models;

models = ({{model.get_pointer_type()}})model_list;

return {{model | model_from_row_result_function_name}}( query, &models[next_model_list_idx] );
}


/**************************************************
*
*    {{model | model_from_row_result_function_name}} - Model from row result
*
*    A cqlite_model_from_row_result_func_t function
*    that reads the provided query row result as a
*    {{model.name}} model.
*
**************************************************/
static int {{model | model_from_row_result_function_name}}
    (
    sqlite3_stmt * query,
    void * model_out
    )
{
int success;
{{model.get_pointer_type()}} model;

success = 1;
model = ({{model.get_pointer_type()}})model_out;

{% for field in model.fields if field.field_type.is_primitive_type() %}
{{field | field_read_result_function_call(model, 'query', 'model', 'success')}}
{% endfor %}

{% for field in model.fields if not field.field_type.is_primitive_type() %}
{{field | field_read_result_function_call(model, 'query', 'model', 'success')}}
{% endfor %}

return success;
}

{% endfor %}