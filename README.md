# cDAL - Data Access Layer for C
The goal of the cDAL project is to simplify the task of creating data access logic for C data types stored in a SQLite database. Often, this code is mechaninal to write but difficult to maintain and evolve as data models are changed and updated. cDAL is **not** meant to be an ORM, but rather simply provide a way to generate the boiler-plate C code necessary to read and write data to and from a SQLite database. cDAL makes a few simplifying assumptions and imposes a few limitations on the data models it supports:
   
   - cDAL assumes that all rows in all database tables can be mapped one-to-one to C structs
   - cDAL assumes that, in the common case, most data access operations work with entire rows rather than only a subset of columns

There are several things cDAL does **not** do:

   - cDAL does not handle relationships between tables
   - cDAL does not handle database transactions or synchronizing multi-threaded access to the database

Instead, cDAL leaves it up to higher-level layers to handle the logic of navigating relationships between models and managing concerns such as transactions and synchronizations. cDAL simply provides a way to generate the code to read and write structs and collections of structs to and from database tables based on definitions of database models.

cDAL aims to simply generate the boiler-plate code to perform the simple common operations on database tables, while still allowing developers to define and perform more complex database operations. The common operations cDAL provides are
   - Writing individual records to a database table
   - Writing collections of records to a database table
   - Retrieving all records from a database table
   - Retrieving collections of records from a database table that match some search criteria
   - Retrieving individual records that match some search criteria
   - Updating records that match some criteria
   - Deleting records that match some criteria

To use cDAL, developers provide a dataset definition JSON file to specify the models that make up their databse. For example, suppose we wanted to store race results in a database, then our dataset definition might look like:
```json
{
    "datasetName": "RaceResults",

    "models": [
        {
            "name": "race",
            "typeName": "race_t",
            "tableName": "races",
            "fields": [
                {
                    "name": "id",
                    "type": "PrimaryKey"
                },
                {
                    "name": "distance",
                    "type": "Real"
                },
                {
                    "name": "name",
                    "type": "Text"
                },
                {
                    "name": "city",
                    "type": "Text"
                },
                {
                    "name": "state",
                    "type": "Text",
                    "maxLength": 3
                }
            ],
            "queries": {
                "select": [
                    {
                        "name": "races_get_all_by_state",
                        "query": "WHERE state = {state:Text}"
                    },
                    {
                        "name": "races_get_all_by_distance",
                        "query": "WHERE distance > {min_distance:Real} AND distance < {max_distance:Real} GROUP BY {state:Text}"
                    },
                ]
            }
        },
        {
            "name": "runner",
            "typeName": "runner_t",
            "tableName": "runners",
            "fields": [
                {
                    "name": "id",
                    "type": "PrimaryKey"
                },
                {
                    "name": "name",
                    "type": "Text"
                },
                {
                    "name": "age",
                    "type": "Integer"
                },
                {
                    "name": "gender",
                    "type": "Text",
                    "maxLength": 2
                }
            ],
            "queries": {
                "select": [
                    {
                        "name": "runners_get_all_by_age_range",
                        "query": "WHERE {min_age:Integer} < age AND age < {max_age:Integer}"
                    },
                    {
                        "name": "runners_get_all_by_gender",
                        "query": "WHERE gender = {gender:Text}"
                    }
                ],
                "count": [
                    {
                        "name": "runners_count_by_age_and_gender",
                        "query": "WHERE gender = {gender:Text} GROUP BY {age:Integer}"
                    }
                ]
            }   
        },
        {
            "name": "race_result",
            "typeName": "race_result_t",
            "tableName": "race_results",
            "fields": [
                {
                    "name": "id",
                    "type": "PrimaryKey"
                },
                {
                    "name": "race_id",
                    "type": "ForeignKey"
                },
                {
                    "name": "runner_id",
                    "type": "ForeignKey"
                },
                {
                    "name": "time_in_seconds",
                    "type": "Integer"
                }
            ],
            "queries": {
                "select": [
                    {
                        "name": "race_results_select_by_race_id",
                        "query": "WHERE race_id = {race_id:ForeignKey}"
                    },
                    {
                        "name": "race_results_select_by_runner_id",
                        "query": "WHERE runner_id = {runner_id:ForeignKey}"
                    }
                ]
            } 
        }
    ]
}

```
From this dataset definition, cDAL would then generation the following C type definitions 
```C
typedef struct
    {
    sqlite3_int64 id;
    double distance;
    char* name;
    char* city;
    char state[ 3 ];
    } race_t;

typedef struct
    {
    race_t* list;
    int cnt;
    } race_list_t;

typedef struct
    {
    sqlite3_int64 id;
    char* name;
    int age;
    char gender[ 2 ];
    } runner_t;

typedef struct
    {
    runner_t* list;
    int cnt;
    } runner_list_t;

typedef struct
    {
    sqlite3_int64 id;
    sqlite3_int64 race_id;
    sqlite3_int64 runner_id;
    int time_in_seconds;
    } race_result_t;

typedef struct
    {
    race_result_t* list;
    int cnt;
    } race_result_list_t;

```
As well as the following data access procedures:
```C
int races_delete_all
    (
    void
    );

int races_get_all
    (
    sqlite3 * db,
    race_list_t * races_out
    );

int races_get_all_by_distance
    (
    double min_distance,
    double max_distance,
    race_list_t * races_out
    );

int races_get_all_by_state
    (
    char const * state,
    race_list_t * races_out
    );

int races_insert_all_new
    (
    race_list_t * races
    );

int races_insert_new
    (
    race_t * race
    );

int races_save_existing
    (
    race_t const * race
    );

int races_save_all_existing
    (
    race_list_t const * races
    );
```