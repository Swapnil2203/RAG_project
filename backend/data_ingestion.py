import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
import re
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import json

# Load environment variables
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
CHRISTMAS_INDEX_NAME = "christmas-index"
SUSTAINABILITY_INDEX_NAME = "sustainability-index"

# Function to load CSV from Azure Blob Storage
def load_csv_from_blob(blob_name, container_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Ensure that blob_name doesn't contain backslashes
    download_file_path = os.path.join("./", blob_name.replace("\\", "/"))  # Replace any backslashes with forward slashes
    
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    return pd.read_csv(download_file_path)

# Example usage
christmas_data = load_csv_from_blob("cleaned_christmas_data.csv", "ragdataset")
sustainability_data = load_csv_from_blob("cleaned_sustainability_data.csv", "ragdataset")


# Step to Remove extra spaces from column names
christmas_data.columns = christmas_data.columns.str.strip()
sustainability_data.columns = sustainability_data.columns.str.strip()

# Create combined headers to handle the nested headers
def create_combined_headers(data):
    # Assuming the first two rows are headers and the first column is also part of the headers
    header_rows = data.loc[0:2].fillna('')
    
    # Combine the first two rows and the first column to create headers
    combined_headers = header_rows.apply(lambda x: ' '.join(x.astype(str)).strip(), axis=0)

    # Replace any empty or invalid header names with a unique placeholder
    combined_headers = [
        col if col.strip() != '' else f"Unnamed_{idx}"
        for idx, col in enumerate(combined_headers)
    ]

    # Assign the combined headers to the dataframe
    data.columns = combined_headers

    # Remove columns with empty or invalid names
    data = data.loc[:, ~data.columns.duplicated()].copy()

    # Remove the header rows from the data
    data = data.iloc[2:].reset_index(drop=True)

    return data

# Remove columns with empty names after combined headers step
christmas_data = christmas_data.loc[:, christmas_data.columns != ""]
sustainability_data = sustainability_data.loc[:, sustainability_data.columns != ""]

# Prepare the data for Azure Cognitive Search ingestion
def prepare_documents_structured(data):
    documents = []

    for i, row in data.iterrows():
        demographics = row.get('Demographics', 'N/A').strip() if isinstance(row.get('Demographics', 'N/A'), str) else 'N/A'
        questions_and_responses = []

        for col in data.columns:
            if col != 'Demographics' and "Unnamed" not in col:  # Skip columns with "Unnamed"
                question = str(col).strip()

                # Clean up the column name to make it a valid identifier
                question = re.sub(r'[^a-zA-Z0-9_]', '_', question)  # Replace non-alphanumeric characters with '_'
                question = re.sub(r'^[^a-zA-Z]+', '', question)

                response = row[col]

                # Convert response to a JSON-serializable format
                if pd.isna(response) or response == " " or response == "":
                    continue  # Skip empty or null responses
                else:
                    response = str(response)  # Convert all responses to strings for consistency

                if question:  # Only add if the question has a valid name
                    questions_and_responses.append({
                        "Question": question,
                        "Response": response
                    })

        # Ensure `QuestionsAndResponses` is neither empty nor null
        if questions_and_responses:
            document = {
                "id": str(i),
                "Demographics": demographics if demographics and demographics != " " else "N/A",
                "QuestionsAndResponses": questions_and_responses
            }

            documents.append(document)

    # Debug step: print the total count of documents and sample documents to verify
    print(f"Total documents prepared: {len(documents)}")
    if len(documents) > 0:
        print("Sample document for ingestion:", json.dumps(documents[0], indent=4))

    return documents

# Prepare documents for both datasets
christmas_documents = prepare_documents_structured(christmas_data)
sustainability_documents = prepare_documents_structured(sustainability_data)

# Azure Cognitive Search client setup
search_client_christmas = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT,
                                       index_name=CHRISTMAS_INDEX_NAME,
                                       credential=AzureKeyCredential(AZURE_SEARCH_API_KEY))

search_client_sustainability = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT,
                                            index_name=SUSTAINABILITY_INDEX_NAME,
                                            credential=AzureKeyCredential(AZURE_SEARCH_API_KEY))

# Ingest documents into Azure Cognitive Search one by one
def ingest_documents_one_by_one(search_client, documents):
    successfully_ingested = 0
    failed_documents = 0

    for doc in documents:
        try:
            # Skip documents with empty or null QuestionsAndResponses
            if not doc.get('QuestionsAndResponses'):
                print(f"Skipping document with ID {doc['id']} due to empty QuestionsAndResponses.")
                continue
            
            result = search_client.upload_documents(documents=[doc])
            if result[0].succeeded:
                successfully_ingested += 1
            else:
                failed_documents += 1
                print(f"Failed to index document ID {doc['id']}: {result[0].error_message}")

        except Exception as e:
            failed_documents += 1
            print(f"Error indexing document ID {doc['id']}: {e}")

    print(f"Ingestion completed successfully. Total successful: {successfully_ingested}, Total failed: {failed_documents}")

# Ingest both datasets
if christmas_documents:
    ingest_documents_one_by_one(search_client_christmas, christmas_documents)
else:
    print("No valid Christmas documents to ingest.")

if sustainability_documents:
    ingest_documents_one_by_one(search_client_sustainability, sustainability_documents)
else:
    print("No valid Sustainability documents to ingest.")