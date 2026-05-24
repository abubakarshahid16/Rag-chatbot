# Use python:3.9-slim as base
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files first for Docker caching
COPY Backend/requirements.txt ./Backend/requirements.txt
COPY Frontend/requirements.txt ./Frontend/requirements.txt

# Install dependencies
RUN pip3 install --no-cache-dir -r ./Backend/requirements.txt
RUN pip3 install --no-cache-dir -r ./Frontend/requirements.txt

# Copy the rest of the application files
COPY Backend/ ./Backend/
COPY Frontend/ ./Frontend/
COPY assets/ ./assets/

# Expose ports (8000 for FastAPI backend, 8501 for Streamlit UI)
EXPOSE 8000
EXPOSE 8501

# Create startup script to run both processes concurrently
RUN printf '#!/bin/bash\n\
uvicorn Backend.main:app --host 0.0.0.0 --port 8000 &\n\
streamlit run Frontend/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start backend and frontend
CMD ["/app/start.sh"]
