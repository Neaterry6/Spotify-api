# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for yt-dlp, tesseract, ffmpeg, pillow, etc.
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    libtesseract-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (to leverage Docker cache)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Expose port 8000
EXPOSE 8000

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]