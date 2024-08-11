# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables to avoid Python buffering and unbuffered logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies required by WeasyPrint
RUN apt-get update \
    && apt-get install -y \
        libpango-1.0-0 \
        libcairo2 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        libgdk-pixbuf2.0-dev \
        libpango1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set the command to run your application
CMD ["python", "app.py"]
