import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory

# Load environment variables
load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = "demo_company_employees"

def get_mongo_client(mongo_uri):
    """Establish connection to the MongoDB and ping the database."""

    # gateway to interacting with a MongoDB database cluster
    client = MongoClient(mongo_uri, appname="devrel.showcase.hr_agent.python")

    # Ping the database to ensure the connection is successful
    try:
        client.admin.command('ping')
        print("Connection to MongoDB successful")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

    return client


def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
  return MongoDBChatMessageHistory(MONGO_URI, session_id, database_name=DATABASE_NAME, collection_name="history")
