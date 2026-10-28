from pymongo import MongoClient
from app.config.settings import settings


# Create MongoDB client
client = MongoClient(settings.MONGODB_URL)

# Select database
database = client[settings.DATABASE_NAME]


# Test MongoDB connection
def check_database_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False