FROM python:3.12-slim

# Install all system dependencies in one RUN block
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-ind \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port (for clarity; Railway handles it)
EXPOSE 8000

# Start FastAPI with uvicorn, using environment PORT if exists, else default to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
