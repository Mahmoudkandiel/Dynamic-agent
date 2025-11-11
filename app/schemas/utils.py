from typing import Optional
from pydantic import BaseModel

class DbSchemaRequest(BaseModel):
    """
    Pydantic model for the schema request.
    db_name is only required if db_type is 'mongo'.
    """
    db_type: str
    connection_string: str
    db_name: Optional[str] = None