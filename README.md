# RAG_Project

## Overview

The RAG (Retrieval-Augmented Generation) Project is designed to create a web application that integrates backend retrieval mechanisms with a React frontend. The backend provides responses to questions posed by users, utilizing retrieval-augmented generation techniques to ensure more relevant and informed responses. This README file will guide you through setting up, starting, and deploying the project.

## Folder Structure

```
RAG_Project/
|-- backend/
|   |-- __pycache__/
|   |-- .dockerignore
|   |-- .env
|   |-- app.py
|   |-- Data_cleaning.ipynb
|   |-- data_ingestion.py
|   |-- data_llm.py
|   |-- data_retrieval.py
|   |-- data_storage.py
|   |-- Dockerfile
|   |-- requirements.txt
|
|-- Datasets/
|
|-- myenv3.10/
|
|-- rag-frontend/
|   |-- node_modules/
|   |-- public/
|   |-- src/
|   |-- .dockerignore
|   |-- .gitignore
|   |-- Dockerfile
|   |-- nginx.conf
|   |-- package-lock.json
|   |-- package.json
|   |-- README.md
```

## Prerequisites

- **Python 3.10**: Backend is developed in Python.
- **Node.js and npm**: To run the frontend React application.
- **Docker**: Used for containerizing both backend and frontend.
- **Azure CLI**: To deploy and manage the project in Azure.

## Backend Setup

1. **Install Dependencies**

   Navigate to the backend directory and install dependencies using:

   ```sh
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Variables**

   Set up your `.env` file in the backend folder, specifying keys like Azure Storage Account Access Key, Azure OpenAI Key, and Azure Search Admin Key.

3. **Run the Backend**

   You can run the backend locally by executing:

   ```sh
   uvicorn app:app --reload
   ```

   This will start the backend on `http://127.0.0.1:8000`.

4. **Docker Setup for Backend**

   Build and run the Docker image for the backend:

   ```sh
   docker build -t rag-backend .
   docker run -p 8000:8000 rag-backend
   ```

## Frontend Setup

1. **Install Dependencies**

   Navigate to the `rag-frontend` directory and run:

   ```sh
   cd rag-frontend
   npm install
   ```

2. **Run the Frontend**

   You can run the frontend locally by executing:

   ```sh
   npm start
   ```

   This will start the frontend on `http://localhost:3000`.

3. **Docker Setup for Frontend**

   Build and run the Docker image for the frontend:

   ```sh
   docker build -t rag-frontend .
   docker run -p 80:80 rag-frontend
   ```

## Deployment to Azure

### Backend Deployment

1. **Push Backend Docker Image**

   Use Docker to build and push the image to your Azure Container Registry:

   ```sh
   docker buildx build --platform linux/amd64 -t rag-backend:latest -f backend/Dockerfile ./backend
   docker push <your-acr>.azurecr.io/rag-backend:latest
   ```

2. **Create Azure Web App**

   ```sh
   az webapp create --resource-group <ResourceGroup> --plan <AppServicePlan> --name rag-backend-app --deployment-container-image-name <your-acr>.azurecr.io/rag-backend:latest
   ```

### Frontend Deployment

1. **Push Frontend Docker Image**

   ```sh
   docker buildx build --platform linux/amd64 -t rag-frontend:latest -f rag-frontend/Dockerfile ./rag-frontend
   docker push <your-acr>.azurecr.io/rag-frontend:latest
   ```

2. **Create Azure Web App**

   ```sh
   az webapp create --resource-group <ResourceGroup> --plan <AppServicePlan> --name rag-frontend-app --deployment-container-image-name <your-acr>.azurecr.io/rag-frontend:latest
   ```

## Troubleshooting

1. **Port Issues**
   - Ensure the correct port is exposed in Dockerfiles (port `8000` for backend, port `80` for frontend).
   - Update Azure Web App configuration settings if needed, ensuring the ports are set correctly (`WEBSITES_PORT`).

2. **Azure Secrets Detected**
   - Before pushing code to GitHub, make sure sensitive information like API keys are not included.
   - Add `.env` files to `.gitignore` to prevent accidental commits.

3. **Backend or Frontend Failing to Start**
   - Review Azure logs using the Azure portal or CLI to check container errors.
   - Ensure `CORS` is configured correctly in the backend to allow requests from the frontend.

## Live Application

You can access the live version of the application here: [RAG Frontend Application](https://rag-frontend-app-bi.azurewebsites.net/)


