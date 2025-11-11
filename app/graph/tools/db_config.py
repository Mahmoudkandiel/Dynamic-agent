from pymongo import MongoClient
from pymongo.errors import PyMongoError
import traceback
from pymongo.uri_parser import parse_uri
import psycopg2
from psycopg2 import extras
from utils import parse_mysql_uri
import mysql.connector
from mysql.connector import errorcode



def mongo_schema(connection_string: str , db_name:str) -> dict:
    """
    Connects to a MongoDB database using the given connection string and db_name and returns:
      1. Success -> all collections and their fields (sampled from one document)
      2. Fail -> error message
    """
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=3000)
        db = client[db_name]

        collections = db.list_collection_names()
        schema = []

        for coll_name in collections:
            collection = db[coll_name]
            sample_doc = collection.find_one()
            if sample_doc:
                fields = {
                    k: type(v).__name__
                    for k, v in sample_doc.items()
                    if k != "_id"
                }
            else:
                fields = {}

            schema.append({
                "name": coll_name,
                "fields": fields
            })

        return {
            "status": "success",
            "database": db_name,
            "collections": schema
        }

    except PyMongoError as e:
        return {"status": "error", "message": str(e)}
    except Exception:
        return {"status": "error", "message": traceback.format_exc()}




def postgres_schema(connection_string: str) -> dict:
    """
    Connects to a PostgreSQL database using the runtime config and returns the schema
    (all tables in the 'public' schema and their columns with data types).
    
    Args:
        runtime (ToolRuntime[AgentConfig]): The runtime context containing the db config.

    Returns:
        dict: { "status": "success", "database": "...", "tables": [...] } 
              or { "status": "error", "message": "..." }
    """
    conn = None

    try:
        # Connect to the database
        conn = psycopg2.connect(connection_string)
        # Get the database name from the connection parameters
        db_name = conn.get_dsn_parameters()
        
        # Create a cursor that returns dictionaries
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            
            # SQL query to get table names, column names, and data types
            # for all tables in the 'public' schema.
            cur.execute("""
                SELECT
                    c.table_name,
                    c.column_name,
                    c.data_type
                FROM
                    information_schema.columns AS c
                JOIN
                    information_schema.tables AS t
                    ON c.table_schema = t.table_schema AND c.table_name = t.table_name
                WHERE
                    c.table_schema = 'public'
                    AND t.table_type = 'BASE TABLE'
                ORDER BY
                    c.table_name, c.ordinal_position;
            """)
            
            results = cur.fetchall()

        # Process the flat list of results into a structured schema
        schema_map = {}
        for row in results:
            table_name = row['table_name']
            if table_name not in schema_map:
                schema_map[table_name] = {
                    "name": table_name,
                    "fields": {}
                }
            schema_map[table_name]["fields"][row['column_name']] = row['data_type']
        
        # Convert the map to the final list format
        schema_list = list(schema_map.values())

        return {
            "status": "success",
            "database": db_name,
            "tables": schema_list
        }

    except (Exception, psycopg2.DatabaseError) as e:
        # Rollback on error (though this is a read-only query)
        if conn:
            conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        # Always close the connection
        if conn:
            conn.close()



def mysql_schema(connection_string : str) -> dict:
    """
    Connects to a MySQL database using the runtime config and returns the schema
    (all tables in the current database and their columns with data types).
    
    Args:
        runtime (ToolRuntime[AgentConfig]): The runtime context containing the db config.

    Returns:
        dict: { "status": "success", "database": "...", "tables": [...] } 
              or { "status": "error", "message": "..." }
    """
    conn = None
    try:
        conn_config = parse_mysql_uri(connection_string)
        db_name = conn_config.get('database')

        try:
            # Connect to the database
            conn = mysql.connector.connect(**conn_config)
            
            # Create a cursor that returns dictionaries
            with conn.cursor(dictionary=True) as cur:
                
                # SQL query to get table names, column names, and data types
                # for all tables in the current database.
                cur.execute("""
                    SELECT
                        c.TABLE_NAME,
                        c.COLUMN_NAME,
                        c.DATA_TYPE
                    FROM
                        information_schema.columns AS c
                    JOIN
                        information_schema.tables AS t
                        ON c.table_schema = t.table_schema AND c.table_name = t.table_name
                    WHERE
                        c.table_schema = DATABASE()
                        AND t.table_type = 'BASE TABLE'
                    ORDER BY
                        c.table_name, c.ordinal_position;
                """)
                
                results = cur.fetchall()

            # Process the flat list of results into a structured schema
            schema_map = {}
            print(results)
            for row in results:
                table_name = row['TABLE_NAME']
                if table_name not in schema_map:
                    schema_map[table_name] = {
                        "name": table_name,
                        "fields": {}
                    }
                schema_map[table_name]["fields"][row['COLUMN_NAME']] = row['DATA_TYPE']
            
            # Convert the map to the final list format
            schema_list = list(schema_map.values())

            return {
                "status": "success",
                "database": db_name,
                "tables": schema_list
            }

        except mysql.connector.Error as err:
            # Rollback on error
            if conn:
                conn.rollback()
            return {"status": "error", "message": f"MySQL Error: {err}"}
        finally:
            # Always close the connection
            if conn and conn.is_connected():
                conn.close()

    except Exception as e:
        # For errors outside the DB connection (e.g., config error)
        return {"status": "error", "message": traceback.format_exc()}


