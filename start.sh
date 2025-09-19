#!/bin/bash

# PostgreSQL MCP Server Startup Script (Client-Only)

set -e

echo "🚀 Starting PostgreSQL MCP Server (Client-Only)..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if PostgreSQL connection environment variables are set
if [ -z "$POSTGRES_HOST" ] || [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ PostgreSQL connection environment variables not set"
    echo ""
    echo "Please set the following environment variables:"
    echo "  POSTGRES_HOST - PostgreSQL host"
    echo "  POSTGRES_PORT - PostgreSQL port (default: 5432)"
    echo "  POSTGRES_DB - Database name"
    echo "  POSTGRES_USER - Username"
    echo "  POSTGRES_PASSWORD - Password"
    echo ""
    echo "Example:"
    echo "  export POSTGRES_HOST=localhost"
    echo "  export POSTGRES_PORT=5432"
    echo "  export POSTGRES_DB=my_database"
    echo "  export POSTGRES_USER=my_user"
    echo "  export POSTGRES_PASSWORD=my_password"
    echo ""
    echo "Or create a .env file with these variables."
    exit 1
fi

# Build the MCP server image
echo "📦 Building PostgreSQL MCP Server image..."
docker-compose build

# Start the MCP server service
echo "🔧 Starting MCP server (connecting to external PostgreSQL)..."
docker-compose up -d postgres-mcp-server

# Wait for the service to be ready
echo "⏳ Waiting for MCP server to be ready..."
sleep 5

# Test the connection (if test script exists)
if [ -f "test.py" ]; then
    echo "🧪 Testing PostgreSQL connection..."
    docker-compose exec postgres-mcp-server python test.py
fi

echo ""
echo "🎉 PostgreSQL MCP Server is ready!"
echo ""
echo "📋 Configuration for Cursor AI:"
echo "Add this to your Cursor MCP configuration:"
echo ""
cat cursor-mcp-config.json
echo ""
echo ""
echo "🔧 Available commands:"
echo "  - View logs: docker-compose logs -f postgres-mcp-server"
echo "  - Stop service: docker-compose down"
echo "  - Test server: docker-compose exec postgres-mcp-server python test.py"
echo ""
echo "📖 Note: This MCP server connects to external PostgreSQL databases."
echo "Make sure your PostgreSQL server is accessible and running."