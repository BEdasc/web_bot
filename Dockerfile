FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./

# Create directory for ChromaDB
RUN mkdir -p /app/chroma_db

# Expose API port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
