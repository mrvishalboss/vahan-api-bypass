# Use the official Playwright image matching your library version
FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY main.py .

# Start the Uvicorn server, using the PORT environment variable injected by your host
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
