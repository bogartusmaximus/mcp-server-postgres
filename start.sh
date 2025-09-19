#!/bin/bash

# PostgreSQL MCP Server Startup Script

set -e

echo "🚀 Starting PostgreSQL MCP Server..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build the MCP server image
echo "📦 Building PostgreSQL MCP Server image..."
docker build -f Dockerfile.postgres-mcp -t postgres-mcp-server .

# Start the services
echo "🔧 Starting PostgreSQL database and MCP server..."
docker-compose -f docker-compose.postgres-mcp.yml up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Test the connection
echo "🧪 Testing database connection..."
docker exec postgres-mcp-db psql -U mcp_user -d mcp_test -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL is ready!"
else
    echo "❌ PostgreSQL connection failed"
    exit 1
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
echo "  - View logs: docker-compose -f docker-compose.postgres-mcp.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose.postgres-mcp.yml down"
echo "  - Test server: python test_postgres_mcp.py"
echo ""
echo "📖 For more information, see README.postgres-mcp.md"
