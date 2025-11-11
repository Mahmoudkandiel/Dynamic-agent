from fastapi import APIRouter, Depends, HTTPException, status

from pydantic import BaseModel
from schemas import DbSchemaRequest
from graph.tools import mongo_schema, postgres_schema, mysql_schema

router = APIRouter(prefix="/utils", tags=["utils"])
@router.post("/db/schema")
async def get_database_schema(
    request: DbSchemaRequest
):
    """
    Connect to a database and retrieve its schema.
    Supported db_types: 'mongo', 'postgres', 'mysql'
    """
    result = {}
    
    try:
        
        if request.db_type == "mongodb":
            if not request.db_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing 'db_name' for db_type 'mongo'"
                )
            result = mongo_schema(
                connection_string=request.connection_string, 
                db_name=request.db_name
            )

        elif request.db_type == "postgres":
            result = postgres_schema(
                connection_string=request.connection_string
            )

        elif request.db_type == "mysql":
            result = mysql_schema(
                connection_string=request.connection_string
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported db_type: '{request.db_type}'. "
                       f"Supported types are 'mongo', 'postgres', 'mysql'."
            )
        
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Unknown database error")
            )
        return result

    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An unexpected error occurred: {str(e)}"
        )