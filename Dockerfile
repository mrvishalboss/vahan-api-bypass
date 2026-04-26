# Microsoft ki official image - Version updated to 1.58.0
FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

# Requirements install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Apna main API code copy karein
COPY main.py .

# Server start karne ka command
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
