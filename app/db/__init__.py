from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://tariqeyego:K0tn94fPWbB3XWKR@eyego.6gk2cxc.mongodb.net/?retryWrites=true&w=majority&appName=eyego")
DB_NAME = os.getenv("DB_NAME", "eyego")
collection_name = os.getenv("COLLECTION_NAME", "agents")


client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
