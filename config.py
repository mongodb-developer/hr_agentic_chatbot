import os

OPEN_AI_EMBEDDING_MODEL = "text-embedding-3-small"
OPEN_AI_EMBEDDING_MODEL_DIMENSION = 256

MONGO_URI = os.environ.get('MONGO_URI')
DATABASE_NAME = 'demo_company_employees'
COLLECTION_NAME = "employees"
COMPANY_COLLECTION_NAME = 'companies'
WORKFORCE_COLLECTION_NAME = 'workforce'
ATLAS_VECTOR_SEARCH_INDEX = 'vector_index'