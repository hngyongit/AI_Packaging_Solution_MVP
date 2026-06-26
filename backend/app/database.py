from pymongo import MongoClient
from app.config import settings

# Vercel's serverless Python runtime has an older OpenSSL.
# tlsInsecure=True / tlsAllowInvalidCertificates avoids TLS handshake failures.
client = MongoClient(
    settings.MONGODB_URI,
    tlsInsecure=True,          # work around SSL: TLSV1_ALERT_INTERNAL_ERROR on Vercel
    serverSelectionTimeoutMS=10000,
)
db = client.get_database()

messages_collection = db["messages"]
conversations_collection = db["conversations"]
