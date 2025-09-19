FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server
COPY postgres-mcp-server.py .

# Make the script executable
RUN chmod +x postgres-mcp-server.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port (if needed for future HTTP interface)
EXPOSE 8000

# Run the MCP server
CMD ["python", "postgres-mcp-server.py"]
