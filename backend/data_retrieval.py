from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

# Load Azure credentials from environment variables
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")

# Define the index names
CHRISTMAS_INDEX_NAME = "christmas-index"
SUSTAINABILITY_INDEX_NAME = "sustainability-index"

# Initialize Azure Cognitive Search clients for each index
search_clients = {
    "christmas": SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=CHRISTMAS_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
    ),
    "sustainability": SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=SUSTAINABILITY_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
    )
}

class DataRetrieval:
    @staticmethod
    def determine_index(question):
        """
        Determine which index to query based on the keywords in the question.
        
        Parameters:
            question (str): The user's query.

        Returns:
            SearchClient: The appropriate Azure Cognitive Search client to use.
        """
        question = question.lower()

        if any(keyword in question for keyword in ["christmas", "holiday", "festive"]):
            return search_clients.get("christmas")
        elif any(keyword in question for keyword in ["sustainability", "environment", "green", "eco", "sustainable"]):
            return search_clients.get("sustainability")
        else:
            # If no specific keywords are matched, return an error message
            raise HTTPException(status_code=404, detail="Unable to determine the relevant index for the provided question.")

    @staticmethod
    def query_azure_search(search_client, question, top_k=5):
        """
        Query Azure Cognitive Search to retrieve relevant documents using semantic search.
        
        Parameters:
            search_client (SearchClient): Azure SearchClient instance.
            question (str): The user's query.
            top_k (int): Number of top search results to retrieve.

        Returns:
            List[dict]: List of search results containing relevant documents.
        """
        if not search_client:
            raise HTTPException(status_code=404, detail="No valid search client available.")

        documents = []

        try:
            # Query Azure Cognitive Search
            search_results = search_client.search(
                search_text=question,
                top=top_k,
                query_type="simple"  # Use simple if semantic is not available
            )
            documents = [doc for doc in search_results]

            # Raise an HTTP error if no documents are found
            if not documents:
                raise HTTPException(status_code=404, detail="No relevant information found for the provided question.")

            return documents

        except HTTPException as e:
            # Re-raise HTTP exceptions for FastAPI to handle properly
            raise e
        except Exception as e:
            # Log the detailed error message for debugging
            print(f"Detailed error during Azure Search: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while querying Azure Search.")

    @staticmethod
    def create_context_from_documents(documents):
        """
        Create a context from the search documents for the RAG pipeline.
        
        Parameters:
            documents (List[dict]): List of documents returned from the Azure Cognitive Search.

        Returns:
            str: A context string generated from the retrieved documents.
        """
        context = ""
        for doc in documents:
            if "content" in doc:
                context += f"{doc['content']} "

            if "QuestionsAndResponses" in doc and doc["QuestionsAndResponses"]:
                context += " ".join(f"{qa['Question']}: {qa['Response']}" for qa in doc["QuestionsAndResponses"]) + "\n"

        return context.strip() if context else "No relevant context found."




# Example usage:
if __name__ == "__main__":
    data_retrieval = DataRetrieval()
    question = "What are the top sustainable brands purchased by respondents?"
    
    # Determine the search client to use
    try:
        client = data_retrieval.determine_index(question)

        # Retrieve documents from Azure Search
        documents = data_retrieval.query_azure_search(client, question)

        # Create context from the retrieved documents
        context = data_retrieval.create_context_from_documents(documents)
        print("Context for LLM: {}".format(context))
    except HTTPException as e:
        print(f"Error: {e.detail}")
