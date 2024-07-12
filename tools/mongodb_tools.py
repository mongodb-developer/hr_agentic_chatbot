from langchain.agents import tool
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from typing import Optional
from config import (
    OPEN_AI_EMBEDDING_MODEL,
    OPEN_AI_EMBEDDING_MODEL_DIMENSION,
    MONGO_URI,
    DATABASE_NAME,
    COLLECTION_NAME,
    COMPANY_COLLECTION_NAME,
    WORKFORCE_COLLECTION_NAME,
    ATLAS_VECTOR_SEARCH_INDEX
)
from tools.google_tools import authenticate, get_document, insert_comment, create_google_doc, send_email
from db_utils import companies_collection, workforce_collection

embedding_model = OpenAIEmbeddings(model=OPEN_AI_EMBEDDING_MODEL, dimensions=OPEN_AI_EMBEDDING_MODEL_DIMENSION)

vector_store_employees = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string=MONGO_URI,
    namespace=f"{DATABASE_NAME}.{COLLECTION_NAME}",
    embedding=embedding_model,
    index_name=ATLAS_VECTOR_SEARCH_INDEX,
    text_key="employee_string"
)

vector_store_companies = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string=MONGO_URI,
    namespace=f"{DATABASE_NAME}.{COMPANY_COLLECTION_NAME}",
    embedding=embedding_model,
    index_name=ATLAS_VECTOR_SEARCH_INDEX,
    text_key="description"
)

vector_store_workforce = MongoDBAtlasVectorSearch.from_connection_string(
    connection_string=MONGO_URI,
    namespace=f"{DATABASE_NAME}.{WORKFORCE_COLLECTION_NAME}",
    embedding=embedding_model,
    index_name=ATLAS_VECTOR_SEARCH_INDEX,
    text_key="employee_string"
)



@tool
def list_companies(limit: int = 10, skip: int = 0, sort_by: str = "company_name", sort_order: int = 1) -> str:
    """
    Retrieves a list of companies from the companies collection.

    Args:
        limit: Integer representing the maximum number of companies to retrieve (default: 10).
        skip: Integer representing the number of companies to skip (for pagination, default: 0).
        sort_by: String representing the field to sort by (default: "company_name").
        sort_order: Integer representing the sort order (1 for ascending, -1 for descending, default: 1).

    Returns:
        A string containing the list of companies if found, or a message indicating no companies were found.
    """
    try:
        # Validate sort_order
        if sort_order not in [1, -1]:
            return "Invalid sort_order. Use 1 for ascending or -1 for descending."

        # Perform the query
        cursor = companies_collection.find().sort(sort_by, sort_order).skip(skip).limit(limit)
        companies = list(cursor)

        if companies:
            result = f"Found {len(companies)} companies:\n\n"
            for company in companies:
                result += f"Name: {company['company_name']}\n"
                result += f"Pay: {company['pay']}\n"
                result += f"Opening Hours: {company['opening_hours']['open']} - {company['opening_hours']['close']}\n"
                result += f"Description: {company['description']}\n"
                result += f"Address: {company['address']}\n\n"
            return result
        else:
            return "No companies found with the given criteria."

    except Exception as e:
        return f"An error occurred while retrieving the list of companies: {str(e)}"

@tool
def search_company(company_name: str) -> str:
    """
    Searches for a company by name in the companies collection.

    Args:
        company_name: String representing the name of the company to search for.

    Returns:
        A string containing the company information if found, or a message indicating the company wasn't found.
    """
    query = {"company_name": {"$regex": company_name, "$options": "i"}}
    company = companies_collection.find_one(query)
    
    if company:
        return f"Company found: {company}"
    else:
        return f"No company found with the name '{company_name}'"

@tool
def search_workforce(first_name: Optional[str] = None, 
                     last_name: Optional[str] = None, 
                     availability_day: Optional[str] = None, 
                     availability_time: Optional[str] = None) -> str:
    """
    Searches for workforce documents based on name, availability day, and availability time.

    Args:
        first_name: Optional string representing the first name to search for.
        last_name: Optional string representing the last name to search for.
        availability_day: Optional string representing the day of availability (e.g., "Monday", "Tuesday").
        availability_time: Optional string representing the time of availability (e.g., "9:00am", "2:00pm").

    Returns:
        A string containing the workforce information if found, or a message indicating no matching records were found.
    """
    query = {}
    if first_name:
        query["first_name"] = {"$regex": first_name, "$options": "i"}
    if last_name:
        query["last_name"] = {"$regex": last_name, "$options": "i"}
    if availability_day:
        query[f"availability_day.{availability_day}"] = {"$exists": True}
    if availability_time:
        query["availability_time.start"] = {"$lte": availability_time}
        query["availability_time.close"] = {"$gte": availability_time}

    results = list(workforce_collection.find(query))
    
    if results:
        return f"Matching workforce records found: {results}"
    else:
        return "No matching workforce records found"

@tool
def lookup_employees(query:str, n=10) -> str:
    "Gathers employee details from a mongodb database"
    print(query)
    result = vector_store_employees.similarity_search_with_score(query=query, k=n)
    return str(result)

tools = [
    lookup_employees, 
    authenticate, 
    get_document, 
    insert_comment, 
    create_google_doc, 
    send_email,
    search_company,
    search_workforce,
    list_companies
]