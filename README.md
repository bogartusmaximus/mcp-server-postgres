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

1. Clone and configure:
```bash
git clone https://github.com/bogartusamximus/mcp-server-postgres.git
cd mcp-server-postgres
```

2. Update `docker-compose.yml` with your PostgreSQL credentials

3. Start services:
```bash
./start.sh
```

4. Configure Cursor AI with `cursor-mcp-config.json`

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