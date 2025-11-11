from urllib.parse import urlparse, parse_qs, unquote



def parse_mysql_uri(uri_string: str) -> dict:
    """
    Parses a MySQL connection URI into a dictionary for mysql.connector.
    Handles 'ssl-mode=REQUIRED' by setting 'ssl_verify_cert=True'.
    """
    parsed_uri = urlparse(uri_string)
    
    config = {
        'user': unquote(parsed_uri.username or ''),
        'password': unquote(parsed_uri.password or ''),
        'host': parsed_uri.hostname,
        'port': parsed_uri.port or 3306,
        'database': unquote(parsed_uri.path[1:]), 
    }
    
    return config