import json
import os
import sys
from tqdm import tqdm

# Ensure the mongodb directory is in the sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from mongodb.connect import get_mongo_client
from utilities import get_embedding

MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = 'demo_company_employees'
company_collection_name = 'companies'
workforce_collection_name = 'workforce'
employee_collection_name= 'employees'

# Function to create a string representation of the employee's key attributes for embedding
def create_employee_string(employee):
    job_details = f"{employee['job_details']['job_title']} in {employee['job_details']['department']}"
    skills = ", ".join(employee['skills'])
    performance_reviews = " ".join([f"Rated {review['rating']} on {review['review_date']}: {review['comments']}" for review in employee['performance_reviews']])
    basic_info = f"{employee['first_name']} {employee['last_name']}, {employee['gender']}, born on {employee['date_of_birth']}"
    work_location = f"Works at {employee['work_location']['nearest_office']}, Remote: {employee['work_location']['is_remote']}"
    notes = employee['notes']

    return f"{basic_info}. Job: {job_details}. Skills: {skills}. Reviews: {performance_reviews}. Location: {work_location}. Notes: {notes}"


# Read JSON data from files
with open('data/companies.json', 'r') as f:
    companies_data = json.load(f)

with open('data/workforce.json', 'r') as f:
    workforce_data = json.load(f)

with open('data/employees.json', 'r') as f:
    employee_data = json.load(f)

# Generate Embeddings for employee data to utilise of vector search functionalities
print("Generating embeddings for employees...")
for employee in tqdm(employee_data):
    employee_string = create_employee_string(employee)
    embedding = get_embedding(employee_string)
    if embedding:
        employee['employee_string'] = employee_string
        employee['embedding'] = embedding

# Connect to MongoDB
mongo_client = get_mongo_client(mongo_uri=MONGO_URI)

if mongo_client:
    # Pymongo client of database and collection
    db = mongo_client.get_database(DATABASE_NAME)
else:
    print("Failed to connect to MongoDB. Exiting...")
    exit(1)

# Insert data into MongoDB
company_collection = db[company_collection_name]
workforce_collection = db[workforce_collection_name]
employee_collection = db[employee_collection_name]

company_collection.insert_many(companies_data)
workforce_collection.insert_many(workforce_data)
employee_collection.insert_many(employee_data)

print("Data has been successfully ingested into MongoDB")

# Close the connection
mongo_client.close()
