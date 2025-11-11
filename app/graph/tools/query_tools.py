from langchain_core.tools import tool
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from langchain.tools import tool, ToolRuntime 
import traceback
import json
import psycopg2
from psycopg2 import extras
from models import AgentConfig
from utils import parse_mysql_uri
import mysql.connector
from mysql.connector import errorcode

@tool
def mongo_query_tool(collection: str, query: str,runtime: ToolRuntime[AgentConfig]) -> dict:
    """
    Queries a MongoDB collection using the existing connection info.

    Args:
        collection (str): The collection to query
        query (str): A JSON string representing the MongoDB query.
                     Example: '{"gender": "male"}'

    Returns:
        dict: { "status": "success", "data": [...] } or { "status": "error", "message": "..." }
    """
    try:
        db_config = runtime.context.database_config
        client = MongoClient(db_config.connection_string, serverSelectionTimeoutMS=3000)
        db = client[db_config.db_name]
        coll = db[collection]

        # Try to parse the query
        try:
            query_dict = json.loads(query)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON query format."}

        # Run the query
        result = list(coll.find(query_dict, {"_id": 0}).limit(10))

        print(f"MongoDB query result: {result}")

        return {"status": "success", "count": len(result), "data": result}

    except PyMongoError as e:
        return {"status": "error", "message": str(e)}
    except Exception:
        return {"status": "error", "message": traceback.format_exc()}
    
@tool
def postgres_query_tool(sql_query: str,runtime: ToolRuntime[AgentConfig]) -> dict:
    """
    Queries a PostgreSQL database using the existing connection info.

    Args:
        sql_query (str): The SQL query to execute.
                         Example: "SELECT name, email FROM users WHERE id = 1"
        runtime (ToolRuntime[AgentConfig]): The runtime context containing the db config.

    Returns:
        dict: { "status": "success", "data": [...] } or { "status": "error", "message": "..." }
    """
    try:
        db_config = runtime.context.database_config

        conn_string = db_config.connection_string
        conn = None
        result_as_dicts = []
        
        try:
            # Connect to the database
            conn = psycopg2.connect(conn_string)
            
            # Create a cursor that returns dictionaries
            with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                
                # Run the query
                cur.execute(sql_query)
                
                # Check if the query was a SELECT or something that returns rows
                if cur.description:
                    result = cur.fetchall()
                    # Convert list of DictRow objects to plain dicts
                    result_as_dicts = [dict(row) for row in result]
                
                # Commit if the query was an INSERT, UPDATE, DELETE, etc.
                conn.commit()

            print(f"PostgreSQL query result: {result_as_dicts}")

            return {"status": "success", "count": len(result_as_dicts), "data": result_as_dicts}

        except (Exception, psycopg2.DatabaseError) as e:
            # Rollback on error
            if conn:
                conn.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            # Always close the connection
            if conn:
                conn.close()

    except Exception as e:
        # For errors outside the DB connection (e.g., config error)
        return {"status": "error", "message": traceback.format_exc()}
    


@tool
def mysql_query_tool(sql_query: str,runtime: ToolRuntime[AgentConfig] ) -> dict:
    """
    Executes a SQL query against a MySQL database using the runtime config.
    Returns the results as a list of dictionaries.

    Args:
        sql_query (str): The SQL query to execute.
        runtime (ToolRuntime[AgentConfig]): The runtime context containing the db config.

    Returns:
        dict: { "status": "success", "data": [...] } or { "status": "error", "message": "..." }
    """
    conn = None
    try:
        db_config = runtime.context.database_config
        conn_string = db_config.connection_string
        conn_config = parse_mysql_uri(conn_string)

        try:
            # Connect to the database
            conn = mysql.connector.connect(**conn_config)
            
            # Create a cursor that returns dictionaries
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql_query)
                
                # Check if the query was an INSERT/UPDATE/DELETE
                if cur.description is None:
                    result = {
                        "status": "success",
                        "message": f"Query executed. {cur.rowcount} rows affected."
                    }
                else:
                    # This was a SELECT query, fetch results
                    rows = cur.fetchall()
                    result = {"status": "success", "data": rows}
            
            # Commit changes (if any)
            conn.commit()
            return result

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
