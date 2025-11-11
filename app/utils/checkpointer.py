from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

client = MongoClient("mongodb+srv://tariqeyego:K0tn94fPWbB3XWKR@eyego.6gk2cxc.mongodb.net/?retryWrites=true&w=majority&appName=eyego")
db = client["eyego"]
langgraph_collection = db["langgraph_checkpoints"]


# Wrap the saver to skip metadata


def get_memory():
    return MongoDBSaver(langgraph_collection)
