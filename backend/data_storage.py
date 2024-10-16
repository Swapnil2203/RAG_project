import pandas as pd
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Azure Storage configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "ragdataset"  # Specify your container name

# Paths to your cleaned CSV files
cleaned_sustainability_path = "./Datasets/cleaned_sustainability_data.csv"
cleaned_christmas_path = "./Datasets/cleaned_christmas_data.csv"  

# Create the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# Check if the container exists, create if it doesn't
try:
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    container_client.get_container_properties()  # This will raise an error if the container doesn't exist
    print(f"Container '{CONTAINER_NAME}' already exists.")
except Exception as e:
    print(f"Container '{CONTAINER_NAME}' does not exist. Creating container.")
    container_client = blob_service_client.create_container(CONTAINER_NAME)
    print(f"Container '{CONTAINER_NAME}' created.")

# Function to upload a file to the specified container
def upload_blob(file_path, blob_name):
    try:
        with open(file_path, "rb") as data:
            blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
            blob_client.upload_blob(data, overwrite=True)  # Set overwrite=True if you want to replace existing blobs
            print(f"Uploaded '{blob_name}' successfully.")
    except Exception as e:
        print(f"Failed to upload '{blob_name}': {e}")

# Upload the cleaned datasets
upload_blob(cleaned_sustainability_path, "cleaned_sustainability_data.csv")
upload_blob(cleaned_christmas_path, "cleaned_christmas_data.csv")

print("All datasets have been uploaded to Azure Blob Storage successfully.")
