FROM python:3.13-slim

WORKDIR /app

# Install system dependencies needed for builds and healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Run API with hot reload for development
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
