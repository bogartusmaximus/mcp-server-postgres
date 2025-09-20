FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies using uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the MCP server
COPY src/mcp-server-postgres.py .

# Make the script executable
RUN chmod +x mcp-server-postgres.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import psycopg2; print('MCP Server is healthy')" || exit 1

# Expose port for potential HTTP interface
EXPOSE 8000

# Run the MCP server using uv
CMD ["uv", "run", "python", "mcp-server-postgres.py"]
