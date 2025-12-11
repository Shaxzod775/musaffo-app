# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code including Firebase credentials
COPY . .

# Set environment variable for Firebase credentials path
ENV FIREBASE_CREDENTIALS_PATH=/app/musaffo-33cf5-firebase-adminsdk-fbsvc-9215754308.json

# Expose port (Cloud Run will provide $PORT)
EXPOSE 8080

# Run the application with gunicorn
CMD exec gunicorn main:app --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0
