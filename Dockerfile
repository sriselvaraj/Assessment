# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy app and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
