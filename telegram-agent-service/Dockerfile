# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Create directories
RUN mkdir -p /app/media /app/data

# Set environment
ENV PYTHONUNBUFFERED=1

# Run service
CMD ["python", "main.py"]
