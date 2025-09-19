# PostgreSQL MCP Server

A Dockerized Micro-Agent Communication Protocol (MCP) server for PostgreSQL database interaction.

## Features

- Database connection management with pooling
- SQL query execution with transaction support
- Table and schema management
- CRUD operations with parameterized queries
- Backup and restore functionality
- Health monitoring and diagnostics
- Cursor AI integration

## Quick Start

### Standalone Usage (Client-Only)

1. Clone the repository:
```bash
git clone https://github.com/bogartusmaximus/mcp-server-postgres.git
cd mcp-server-postgres
```

2. Configure environment variables for your PostgreSQL connection:
```bash
export POSTGRES_HOST=your-postgres-host
export POSTGRES_PORT=5432
export POSTGRES_DB=your-database
export POSTGRES_USER=your-username
export POSTGRES_PASSWORD=your-password
```

3. Start the MCP server:
```bash
./start.sh
```

4. Configure Cursor AI with `cursor-mcp-config.json`

### Integration with Existing Projects

This MCP server is designed to be integrated into existing projects that already have PostgreSQL databases. It connects as a client to external PostgreSQL instances and does not provide its own database server.

## Available MCP Tools

- Connection: `postgres_connect`, `postgres_disconnect`, `postgres_health_check`
- Queries: `postgres_execute_query`, `postgres_fetch_data`, `postgres_count_records`
- Tables: `postgres_create_table`, `postgres_drop_table`, `postgres_list_tables`, `postgres_describe_table`
- Data: `postgres_insert_data`, `postgres_update_data`, `postgres_delete_data`, `postgres_backup_table`

## Configuration

Set these environment variables in `docker-compose.yml`:
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port (default: 5432)
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Username
- `POSTGRES_PASSWORD` - Password

## Testing

```bash
docker-compose up -d
python test.py
```

## License

MIT License