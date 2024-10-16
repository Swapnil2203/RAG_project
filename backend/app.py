from fastapi import FastAPI, HTTPException
from typing import Optional
from data_llm import DataLLM
from data_retrieval import DataRetrieval
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)

# Create FastAPI application instance
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with specific domains for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an instance of the DataLLM class
data_llm = DataLLM()

# Create an instance of the DataRetrieval class
data_retrieval = DataRetrieval()

# Define endpoint for interacting with the RAG pipeline
@app.get("/query/")
async def get_query_results(question: Optional[str] = None):
    if not question:
        raise HTTPException(status_code=400, detail="Question parameter cannot be empty.")

    try:
        logging.info("Received question: %s", question)
        # Step 1: Determine which Azure Cognitive Search index to query
        search_clients = data_retrieval.determine_index(question)
        print(search_clients)
        logging.info("Determined search index for query.")

        # Step 2: Query the Azure Cognitive Search service
        search_documents = data_retrieval.query_azure_search(search_clients, question)
        logging.info("Queried Azure Search and received documents.")

        # Step 3: If no relevant documents are found, return a 404 error
        if not search_documents:
            raise HTTPException(status_code=404, detail="No relevant information found for the provided question.")

        # Step 4: Create a context string from retrieved documents for LLM
        context = data_retrieval.create_context_from_documents(search_documents)
        logging.info("Created context for LLM.")

        # Step 5: Use Azure OpenAI to generate an answer based on the given context
        response = DataLLM.query_openai(question=question,context=context)
        logging.info("Received response from OpenAI LLM.")

        # Step 6: Return the generated response to the client
        return {"response": response}

    except HTTPException as http_ex:
        logging.error("HTTPException: %s", str(http_ex))
        raise http_ex
    except Exception as generic_ex:
        logging.error("Unexpected error: %s", str(generic_ex))
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(generic_ex)}")


# Example usage of FastAPI:
# Run the server using `uvicorn app:app --reload`.
