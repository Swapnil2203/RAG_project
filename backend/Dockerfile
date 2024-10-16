# Use the official Python image as a base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install libcurl development package
RUN apt-get update && apt-get install -y libcurl4-openssl-dev


# Copy requirements file and install dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the entire backend folder into the container
COPY backend /app/backend

# Change the working directory to the backend folder
WORKDIR /app/backend


# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the backend application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
