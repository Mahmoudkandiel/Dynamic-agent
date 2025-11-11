from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["eyego"]
langgraph_collection = db["langgraph_checkpoints"]


# Wrap the saver to skip metadata


def get_memory():
    return MongoDBSaver(langgraph_collection)
