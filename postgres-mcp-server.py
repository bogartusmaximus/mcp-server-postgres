#!/usr/bin/env python3
"""
PostgreSQL MCP Server for Cursor AI
Provides tools for interacting with PostgreSQL databases from Cursor AI
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLMCPServer:
    """MCP Server for PostgreSQL database operations"""
    
    def __init__(self):
        self.server = Server("postgres-mcp-server")
        self.connections: Dict[str, psycopg2.extensions.connection] = {}
        self.setup_tools()
    
    def setup_tools(self):
        """Register all available tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List all available PostgreSQL tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="postgres_connect",
                        description="Connect to a PostgreSQL database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "host": {"type": "string", "description": "Database host"},
                                "port": {"type": "integer", "description": "Database port", "default": 5432},
                                "database": {"type": "string", "description": "Database name"},
                                "user": {"type": "string", "description": "Username"},
                                "password": {"type": "string", "description": "Password"},
                                "connection_name": {"type": "string", "description": "Name for this connection", "default": "default"}
                            },
                            "required": ["host", "database", "user", "password"]
                        }
                    ),
                    Tool(
                        name="postgres_disconnect",
                        description="Disconnect from a PostgreSQL database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "connection_name": {"type": "string", "description": "Connection name to disconnect", "default": "default"}
                            }
                        }
                    ),
                    Tool(
                        name="postgres_list_connections",
                        description="List all active database connections",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="postgres_execute_query",
                        description="Execute a SQL query on the database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "SQL query to execute"},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "fetch_results": {"type": "boolean", "description": "Whether to fetch and return results", "default": True},
                                "limit": {"type": "integer", "description": "Limit number of results returned", "default": 1000}
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="postgres_list_tables",
                        description="List all tables in the database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"}
                            }
                        }
                    ),
                    Tool(
                        name="postgres_describe_table",
                        description="Get detailed information about a table structure",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"}
                            },
                            "required": ["table_name"]
                        }
                    ),
                    Tool(
                        name="postgres_table_data",
                        description="Get data from a table with optional filtering",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"},
                                "limit": {"type": "integer", "description": "Number of rows to return", "default": 100},
                                "offset": {"type": "integer", "description": "Number of rows to skip", "default": 0},
                                "where_clause": {"type": "string", "description": "WHERE clause for filtering"},
                                "order_by": {"type": "string", "description": "ORDER BY clause"}
                            },
                            "required": ["table_name"]
                        }
                    ),
                    Tool(
                        name="postgres_create_table",
                        description="Create a new table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "columns": {"type": "array", "description": "Column definitions", "items": {"type": "object"}},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"},
                                "if_not_exists": {"type": "boolean", "description": "Use IF NOT EXISTS", "default": True}
                            },
                            "required": ["table_name", "columns"]
                        }
                    ),
                    Tool(
                        name="postgres_drop_table",
                        description="Drop a table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"},
                                "cascade": {"type": "boolean", "description": "Use CASCADE", "default": False},
                                "if_exists": {"type": "boolean", "description": "Use IF EXISTS", "default": True}
                            },
                            "required": ["table_name"]
                        }
                    ),
                    Tool(
                        name="postgres_insert_data",
                        description="Insert data into a table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "data": {"type": "array", "description": "Data to insert", "items": {"type": "object"}},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"},
                                "on_conflict": {"type": "string", "description": "ON CONFLICT action (DO NOTHING, DO UPDATE)"}
                            },
                            "required": ["table_name", "data"]
                        }
                    ),
                    Tool(
                        name="postgres_update_data",
                        description="Update data in a table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "data": {"type": "object", "description": "Data to update"},
                                "where_clause": {"type": "string", "description": "WHERE clause for filtering"},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"}
                            },
                            "required": ["table_name", "data", "where_clause"]
                        }
                    ),
                    Tool(
                        name="postgres_delete_data",
                        description="Delete data from a table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "where_clause": {"type": "string", "description": "WHERE clause for filtering"},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"}
                            },
                            "required": ["table_name", "where_clause"]
                        }
                    ),
                    Tool(
                        name="postgres_backup_table",
                        description="Create a backup of a table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {"type": "string", "description": "Name of the table"},
                                "backup_table_name": {"type": "string", "description": "Name for backup table"},
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"},
                                "schema": {"type": "string", "description": "Schema name", "default": "public"}
                            },
                            "required": ["table_name", "backup_table_name"]
                        }
                    ),
                    Tool(
                        name="postgres_health_check",
                        description="Check database connection health",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "connection_name": {"type": "string", "description": "Connection name", "default": "default"}
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "postgres_connect":
                    return await self.connect_database(arguments)
                elif name == "postgres_disconnect":
                    return await self.disconnect_database(arguments)
                elif name == "postgres_list_connections":
                    return await self.list_connections(arguments)
                elif name == "postgres_execute_query":
                    return await self.execute_query(arguments)
                elif name == "postgres_list_tables":
                    return await self.list_tables(arguments)
                elif name == "postgres_describe_table":
                    return await self.describe_table(arguments)
                elif name == "postgres_table_data":
                    return await self.get_table_data(arguments)
                elif name == "postgres_create_table":
                    return await self.create_table(arguments)
                elif name == "postgres_drop_table":
                    return await self.drop_table(arguments)
                elif name == "postgres_insert_data":
                    return await self.insert_data(arguments)
                elif name == "postgres_update_data":
                    return await self.update_data(arguments)
                elif name == "postgres_delete_data":
                    return await self.delete_data(arguments)
                elif name == "postgres_backup_table":
                    return await self.backup_table(arguments)
                elif name == "postgres_health_check":
                    return await self.health_check(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def connect_database(self, args: Dict[str, Any]) -> CallToolResult:
        """Connect to a PostgreSQL database"""
        connection_name = args.get("connection_name", "default")
        
        try:
            conn = psycopg2.connect(
                host=args["host"],
                port=args.get("port", 5432),
                database=args["database"],
                user=args["user"],
                password=args["password"]
            )
            
            self.connections[connection_name] = conn
            logger.info(f"Connected to database {args['database']} on {args['host']}")
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Successfully connected to database '{args['database']}' on {args['host']}:{args.get('port', 5432)} as '{args['user']}'"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to connect: {str(e)}")]
            )
    
    async def disconnect_database(self, args: Dict[str, Any]) -> CallToolResult:
        """Disconnect from a PostgreSQL database"""
        connection_name = args.get("connection_name", "default")
        
        if connection_name in self.connections:
            self.connections[connection_name].close()
            del self.connections[connection_name]
            return CallToolResult(
                content=[TextContent(type="text", text=f"Disconnected from '{connection_name}'")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"No connection found for '{connection_name}'")]
            )
    
    async def list_connections(self, args: Dict[str, Any]) -> CallToolResult:
        """List all active connections"""
        if not self.connections:
            return CallToolResult(
                content=[TextContent(type="text", text="No active connections")]
            )
        
        connections_info = []
        for name, conn in self.connections.items():
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT current_database(), current_user, version()")
                    db_name, user, version = cursor.fetchone()
                    connections_info.append(f"- {name}: {db_name} as {user}")
            except Exception as e:
                connections_info.append(f"- {name}: Error getting info - {str(e)}")
        
        return CallToolResult(
            content=[TextContent(type="text", text="Active connections:\n" + "\n".join(connections_info))]
        )
    
    async def execute_query(self, args: Dict[str, Any]) -> CallToolResult:
        """Execute a SQL query"""
        connection_name = args.get("connection_name", "default")
        query = args["query"]
        fetch_results = args.get("fetch_results", True)
        limit = args.get("limit", 1000)
        
        if connection_name not in self.connections:
            return CallToolResult(
                content=[TextContent(type="text", text=f"No connection found for '{connection_name}'")]
            )
        
        try:
            conn = self.connections[connection_name]
            with conn.cursor() as cursor:
                cursor.execute(query)
                
                if fetch_results and cursor.description:
                    # Fetch results
                    results = cursor.fetchmany(limit)
                    columns = [desc[0] for desc in cursor.description]
                    
                    # Format results as table
                    if results:
                        # Create header
                        header = " | ".join(f"{col:>15}" for col in columns)
                        separator = "-" * len(header)
                        
                        # Create rows
                        rows = []
                        for row in results:
                            row_str = " | ".join(f"{str(val):>15}" for val in row)
                            rows.append(row_str)
                        
                        result_text = f"Query executed successfully. {len(results)} rows returned:\n\n"
                        result_text += header + "\n" + separator + "\n"
                        result_text += "\n".join(rows)
                        
                        if len(results) == limit:
                            result_text += f"\n\n(Results limited to {limit} rows)"
                    else:
                        result_text = "Query executed successfully. No rows returned."
                else:
                    conn.commit()
                    result_text = f"Query executed successfully. {cursor.rowcount} rows affected."
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Query failed: {str(e)}")]
            )
    
    async def list_tables(self, args: Dict[str, Any]) -> CallToolResult:
        """List all tables in the database"""
        connection_name = args.get("connection_name", "default")
        schema = args.get("schema", "public")
        
        query = """
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = %s
        ORDER BY table_name
        """
        
        return await self.execute_query({
            "connection_name": connection_name,
            "query": query,
            "fetch_results": True
        })
    
    async def describe_table(self, args: Dict[str, Any]) -> CallToolResult:
        """Get detailed table information"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        schema = args.get("schema", "public")
        
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """
        
        return await self.execute_query({
            "connection_name": connection_name,
            "query": query,
            "fetch_results": True
        })
    
    async def get_table_data(self, args: Dict[str, Any]) -> CallToolResult:
        """Get data from a table"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        schema = args.get("schema", "public")
        limit = args.get("limit", 100)
        offset = args.get("offset", 0)
        where_clause = args.get("where_clause", "")
        order_by = args.get("order_by", "")
        
        # Build query
        query = f"SELECT * FROM {schema}.{table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        query += f" LIMIT {limit} OFFSET {offset}"
        
        return await self.execute_query({
            "connection_name": connection_name,
            "query": query,
            "fetch_results": True
        })
    
    async def create_table(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new table"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        schema = args.get("schema", "public")
        columns = args["columns"]
        if_not_exists = args.get("if_not_exists", True)
        
        # Build column definitions
        column_defs = []
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            if col.get('not_null'):
                col_def += " NOT NULL"
            if col.get('default'):
                col_def += f" DEFAULT {col['default']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            column_defs.append(col_def)
        
        # Build CREATE TABLE statement
        if_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        query = f"CREATE TABLE {if_exists_clause}{schema}.{table_name} ({', '.join(column_defs)})"
        
        return await self.execute_query({
            "connection_name": connection_name,
            "query": query,
            "fetch_results": False
        })
    
    async def drop_table(self, args: Dict[str, Any]) -> CallToolResult:
        """Drop a table"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        schema = args.get("schema", "public")
        cascade = args.get("cascade", False)
        if_exists = args.get("if_exists", True)
        
        if_exists_clause = "IF EXISTS " if if_exists else ""
        cascade_clause = " CASCADE" if cascade else ""
        query = f"DROP TABLE {if_exists_clause}{schema}.{table_name}{cascade_clause}"
        
        return await self.execute_query({
            "connection_name": connection_name,
            "query": query,
            "fetch_results": False
        })
    
    async def insert_data(self, args: Dict[str, Any]) -> CallToolResult:
        """Insert data into a table"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        schema = args.get("schema", "public")
        data = args["data"]
        on_conflict = args.get("on_conflict")
        
        if not data:
            return CallToolResult(
                content=[TextContent(type="text", text="No data provided")]
            )
        
        # Get column names from first row
        columns = list(data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        
        query = f"INSERT INTO {schema}.{table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        if on_conflict:
            query += f" ON CONFLICT {on_conflict}"
        
        try:
            conn = self.connections[connection_name]
            with conn.cursor() as cursor:
                for row in data:
                    values = [row[col] for col in columns]
                    cursor.execute(query, values)
                
                conn.commit()
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Successfully inserted {len(data)} rows")]
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Insert failed: {str(e)}")]
            )
    
    async def update_data(self, args: Dict[str, Any]) -> CallToolResult:
        """Update data in a table"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        schema = args.get("schema", "public")
        data = args["data"]
        where_clause = args["where_clause"]
        
        # Build SET clause
        set_clauses = [f"{col} = %s" for col in data.keys()]
        query = f"UPDATE {schema}.{table_name} SET {', '.join(set_clauses)} WHERE {where_clause}"
        
        try:
            conn = self.connections[connection_name]
            with conn.cursor() as cursor:
                values = list(data.values())
                cursor.execute(query, values)
                conn.commit()
                
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Successfully updated {cursor.rowcount} rows")]
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Update failed: {str(e)}")]
            )
    
    async def delete_data(self, args: Dict[str, Any]) -> CallToolResult:
        """Delete data from a table"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        schema = args.get("schema", "public")
        where_clause = args["where_clause"]
        
        query = f"DELETE FROM {schema}.{table_name} WHERE {where_clause}"
        
        return await self.execute_query({
            "connection_name": connection_name,
            "query": query,
            "fetch_results": False
        })
    
    async def backup_table(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a backup of a table"""
        connection_name = args.get("connection_name", "default")
        table_name = args["table_name"]
        backup_table_name = args["backup_table_name"]
        schema = args.get("schema", "public")
        
        query = f"CREATE TABLE {schema}.{backup_table_name} AS SELECT * FROM {schema}.{table_name}"
        
        return await self.execute_query({
            "connection_name": connection_name,
            "query": query,
            "fetch_results": False
        })
    
    async def health_check(self, args: Dict[str, Any]) -> CallToolResult:
        """Check database connection health"""
        connection_name = args.get("connection_name", "default")
        
        if connection_name not in self.connections:
            return CallToolResult(
                content=[TextContent(type="text", text=f"No connection found for '{connection_name}'")]
            )
        
        try:
            conn = self.connections[connection_name]
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                if result[0] == 1:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Connection '{connection_name}' is healthy")]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Connection '{connection_name}' health check failed")]
                    )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Health check failed: {str(e)}")]
            )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="postgres-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point"""
    server = PostgreSQLMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
