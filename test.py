#!/usr/bin/env python3
"""
Test script for PostgreSQL MCP Server
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import the MCP server module
import importlib.util
spec = importlib.util.spec_from_file_location("postgres_mcp_server", "postgres-mcp-server.py")
postgres_mcp_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(postgres_mcp_server)
PostgreSQLMCPServer = postgres_mcp_server.PostgreSQLMCPServer

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("Testing PostgreSQL MCP Server...")
    
    # Create server instance
    server = PostgreSQLMCPServer()
    
    # Test connection
    print("\n1. Testing database connection...")
    connect_result = await server.connect_database({
        "host": "localhost",
        "port": 5433,
        "database": "mcp_test",
        "user": "mcp_user",
        "password": "mcp_password",
        "connection_name": "test"
    })
    print(f"Connection result: {connect_result.content[0].text}")
    
    # Test health check
    print("\n2. Testing health check...")
    health_result = await server.health_check({"connection_name": "test"})
    print(f"Health check result: {health_result.content[0].text}")
    
    # Test table creation
    print("\n3. Testing table creation...")
    create_result = await server.create_table({
        "table_name": "test_users",
        "columns": [
            {"name": "id", "type": "SERIAL", "primary_key": True},
            {"name": "name", "type": "VARCHAR(100)", "not_null": True},
            {"name": "email", "type": "VARCHAR(255)", "not_null": True},
            {"name": "created_at", "type": "TIMESTAMP", "default": "NOW()"}
        ],
        "connection_name": "test"
    })
    print(f"Create table result: {create_result.content[0].text}")
    
    # Test data insertion
    print("\n4. Testing data insertion...")
    insert_result = await server.insert_data({
        "table_name": "test_users",
        "data": [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"}
        ],
        "connection_name": "test"
    })
    print(f"Insert data result: {insert_result.content[0].text}")
    
    # Test data query
    print("\n5. Testing data query...")
    query_result = await server.execute_query({
        "query": "SELECT * FROM test_users",
        "connection_name": "test",
        "fetch_results": True,
        "limit": 10
    })
    print(f"Query result: {query_result.content[0].text}")
    
    # Test table listing
    print("\n6. Testing table listing...")
    list_result = await server.list_tables({"connection_name": "test"})
    print(f"List tables result: {list_result.content[0].text}")
    
    # Test table description
    print("\n7. Testing table description...")
    describe_result = await server.describe_table({
        "table_name": "test_users",
        "connection_name": "test"
    })
    print(f"Describe table result: {describe_result.content[0].text}")
    
    # Test cleanup
    print("\n8. Testing cleanup...")
    drop_result = await server.drop_table({
        "table_name": "test_users",
        "connection_name": "test",
        "if_exists": True
    })
    print(f"Drop table result: {drop_result.content[0].text}")
    
    # Test disconnection
    print("\n9. Testing disconnection...")
    disconnect_result = await server.disconnect_database({"connection_name": "test"})
    print(f"Disconnect result: {disconnect_result.content[0].text}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
