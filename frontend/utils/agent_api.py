import requests
import time

BASE_URL = "http://Backend:8000"

def get_agents(retries=5, delay=3):
    for i in range(retries):
        try:
            res = requests.get(f"{BASE_URL}/agents")
            return res.json()
        except requests.exceptions.ConnectionError:
            print(f"Backend not ready, retrying ({i+1}/{retries})...")
            time.sleep(delay)
    return []


def create_agent(data):
    res = requests.post(f"{BASE_URL}/agents", json=data)
    res.raise_for_status()
    return res.json()

def delete_agent(agent_id):
    res = requests.delete(f"{BASE_URL}/agents/{agent_id}")
    res.raise_for_status()

def get_config_options(provider=None):
    url = f"{BASE_URL}/agents/config/options"
    if provider:
        url += f"?provider={provider}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def update_agent(agent_id, data):
    res = requests.put(f"{BASE_URL}/agents/{agent_id}", json=data)
    res.raise_for_status()
    return res.json()

def get_agent(agent_id: str):
    """
    Fetches a single agent object by its ID.
    Corresponds to the GET /agents/{agent_id} endpoint.
    """
    res = requests.get(f"{BASE_URL}/agents/{agent_id}")
    res.raise_for_status()
    return res.json()

def get_db_schema(db_type: str ,connection_string: str, db_name: str):
    """
    Fetches the schema of a MongoDB database using the utils API.

    Args:
        connection_string (str): The MongoDB connection string.
        db_name (str): The name of the database.

    Returns:
        dict: The response containing collections and their fields.
    """
    payload = {
        "db_type": db_type,
        "connection_string": connection_string,
        "db_name": db_name
    }
    print("Requesting DB schema with payload:", payload)
    res = requests.post(f"{BASE_URL}/utils/db/schema", json=payload)
    res.raise_for_status()
    return res.json()