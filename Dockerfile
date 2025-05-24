# Use official slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only required system dependencies (minimizing build size)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Optimize pip installations
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose FastAPI’s default port
EXPOSE 8000

# Set Uvicorn to run efficiently with workers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]