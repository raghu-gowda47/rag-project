# Multi-stage build for RAG Chatbot
FROM python:3.10-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY Ramayana.pdf .

# Create volume for vector store persistence
VOLUME /app/chroma_db_bpe

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=host.docker.internal:11434

# Run the chatbot
CMD ["python", "src/main.py"]
