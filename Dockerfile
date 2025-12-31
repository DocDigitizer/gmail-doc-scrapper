# Gmail Document Scraper - Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy Portuguese model
RUN python -m spacy download pt_core_news_lg

# Copy application code
COPY . .

# Create directories
RUN mkdir -p output logs reports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
