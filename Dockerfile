# Base image - Version 1.58.0
FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

# Work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python code
COPY main.py .

# Run the app with extra timeout
CMD uvicorn main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 120
