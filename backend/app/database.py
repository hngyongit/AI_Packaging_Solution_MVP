from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGODB_URI)
db = client.get_database()

messages_collection = db["messages"]
conversations_collection = db["conversations"]
