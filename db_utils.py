from mongodb.connect import get_mongo_client
from config import MONGO_URI, DATABASE_NAME, COMPANY_COLLECTION_NAME, WORKFORCE_COLLECTION_NAME

mongo_client = get_mongo_client(MONGO_URI)
db = mongo_client.get_database(DATABASE_NAME)
companies_collection = db.get_collection(COMPANY_COLLECTION_NAME)
workforce_collection = db.get_collection(WORKFORCE_COLLECTION_NAME)