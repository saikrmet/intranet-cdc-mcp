# Minimal Python image with build stage for faster installs
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies required for building cryptography / ntlm / lxml related packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY main.py models.py client.py ./

# Non-root user (optional)
RUN useradd -u 1001 -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Environment variable documentation:
#   CDC_NTLM_USERNAME - your NTLM username (without domain) or domain\\user combined
#   CDC_NTLM_PASSWORD - password
#   CDC_NTLM_DOMAIN   - optional domain, appended automatically if both set
#   PORT              - port to expose (default 8000)

ENTRYPOINT ["python", "main.py"]

# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential gcc libxml2-dev libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (FastMCP default is 8000)
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "main.py"]
