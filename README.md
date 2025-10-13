# FastAPI TDD Docker Project

A FastAPI application with PostgreSQL database, containerized with Docker and orchestrated with Docker Compose, designed for Test-Driven Development (TDD) workflows using Tortoise ORM for async database operations.

## Project Structure

```
fastapi-tdd-docker/
├── docker-compose.yml          # Docker Compose configuration
├── project/                    # Application source code
│   ├── Dockerfile             # Docker image definition
│   ├── requirements.txt       # Python dependencies
│   ├── .dockerignore         # Docker ignore patterns
│   ├── entrypoint.sh         # Container startup script
│   ├── pyproject.toml        # Aerich migration configuration
│   ├── db/                   # Database configuration
│   │   ├── Dockerfile        # PostgreSQL custom image
│   │   └── create.sql        # Database initialization
│   ├── migrations/           # Database migration files
│   │   └── models/          # Generated migration scripts
│   └── app/                 # FastAPI application
│       ├── __init__.py
│       ├── main.py          # Main application file
│       ├── config.py        # Configuration settings
│       ├── db.py            # Tortoise ORM configuration
│       └── models/          # Database models
│           ├── __init__.py
│           └── tortoise.py  # Tortoise ORM models
└── README.md                # This file
```

## Features

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **PostgreSQL**: Robust relational database with async support
- **Tortoise ORM**: Async ORM inspired by Django ORM for FastAPI
- **Database Migrations**: Automated schema management with Aerich
- **Docker**: Containerized application for consistent development and deployment
- **Docker Compose**: Multi-container orchestration for local development
- **Environment Configuration**: Configurable settings using Pydantic Settings
- **Hot Reload**: Automatic code reloading during development
- **Python 3.13**: Latest Python version with slim base image

## Technology Stack

- **Backend**: FastAPI (Python 3.13)
- **Database**: PostgreSQL 17
- **ORM**: Tortoise ORM with async support
- **Migration Tool**: Aerich
- **Containerization**: Docker & Docker Compose
- **Database Driver**: asyncpg

## Prerequisites

Make sure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or higher)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-tdd-docker
```

### 2. Build and Start the Application

```bash
# Build the Docker image and start the application
docker-compose up --build
```

### 3. Access the Application

Once the container is running, you can access:

- **API Endpoint**: http://localhost:8004/ping
- **Interactive API Documentation**: http://localhost:8004/docs
- **Alternative API Documentation**: http://localhost:8004/redoc

## Services

The application consists of two main services:

- **web**: FastAPI application server
- **web-db**: PostgreSQL database server

## Docker Compose Commands

### Build the Application

```bash
# Build all services
docker-compose build

# Build without using cache
docker-compose build --no-cache

# Build specific service
docker-compose build web
docker-compose build web-db
```

### Start the Application

```bash
# Start all services in foreground (with logs)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start with rebuild
docker-compose up --build

# Start specific service
docker-compose up web-db  # Database only
```

### Stop the Application

```bash
# Stop the running containers
docker-compose down

# Stop and remove volumes (if any)
docker-compose down -v

# Stop and remove everything (containers, networks, images)
docker-compose down --rmi all
```

### View Logs

```bash
# View logs from all services
docker-compose logs

# View logs from specific service
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web
```

### Other Useful Commands

```bash
# List running containers
docker-compose ps

# Execute commands in running container
docker-compose exec web bash

# Restart services
docker-compose restart

# Pull latest images
docker-compose pull
```

## Development

### Environment Variables

The application uses environment variables for configuration:

- `ENVIRONMENT`: Application environment (default: "dev")
- `TESTING`: Testing mode flag (default: 0)
- `DATABASE_URL`: PostgreSQL connection string for development
- `DATABASE_TEST_URL`: PostgreSQL connection string for testing

These can be modified in the `docker-compose.yml` file under the `environment` section.

### Database Models

The project includes a sample `TextSummary` model demonstrating Tortoise ORM usage:

```python
class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
```

### Hot Reload

The application is configured with `--reload` flag and volume mounting, so any changes to the code will automatically restart the server.

### Adding Dependencies

1. Add new packages to `project/requirements.txt`
2. Rebuild the container:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Database Management

#### Initial Setup

The PostgreSQL database is automatically initialized with two databases:

- `web_dev`: Development database
- `web_test`: Testing database

#### Quick Database Commands Reference

```bash
# Connect to development database
docker-compose exec web-db psql -U postgres -d web_dev

# Connect and run a quick command
docker-compose exec web-db psql -U postgres -d web_dev -c "\dt"

# Check database status
docker-compose exec web-db pg_isready -U postgres

# View database logs
docker-compose logs web-db

# Restart database service
docker-compose restart web-db
```

#### Database Migrations

The project uses Aerich for database migrations with Tortoise ORM:

```bash
# Initialize migrations (already done)
docker-compose exec web aerich init -t app.db.TORTOISE_ORM

# Create a new migration after model changes
docker-compose exec web aerich migrate

# Apply migrations
docker-compose exec web aerich upgrade

# Rollback migrations
docker-compose exec web aerich downgrade

# Show migration history
docker-compose exec web aerich history
```

#### Direct Database Access

```bash
# Connect to PostgreSQL directly
docker-compose exec web-db psql -U postgres -d web_dev

# Connect to test database
docker-compose exec web-db psql -U postgres -d web_test

# Connect to default postgres database
docker-compose exec web-db psql -U postgres

# Run SQL commands directly
docker-compose exec web-db psql -U postgres -d web_dev -c "SELECT * FROM textsummary;"
```

#### PostgreSQL Interactive Commands

Once connected with `docker-compose exec web-db psql -U postgres`, you can use these commands:

**Database Operations:**

```sql
-- List all databases
\l

-- Connect to a specific database
\c web_dev
\c web_test

-- Show current database
SELECT current_database();

-- Show database size
SELECT pg_size_pretty(pg_database_size('web_dev'));
```

**Table Operations:**

```sql
-- List all tables in current database
\dt

-- Describe table structure
\d textsummary

-- List all tables with details
\dt+

-- Show table indexes
\di

-- Show table size
SELECT pg_size_pretty(pg_total_relation_size('textsummary'));
```

**Schema and Data Operations:**

```sql
-- Show all schemas
\dn

-- List all functions
\df

-- Show table permissions
\dp

-- Display table data with formatting
SELECT * FROM textsummary;

-- Count records
SELECT COUNT(*) FROM textsummary;

-- Show recent records
SELECT * FROM textsummary ORDER BY created_at DESC LIMIT 5;
```

**Connection and System Info:**

```sql
-- Show current connections
\conninfo

-- List active connections
SELECT * FROM pg_stat_activity;

-- Show PostgreSQL version
SELECT version();

-- Exit psql
\q
```

#### Database Backup and Restore

```bash
# Create database backup
docker-compose exec web-db pg_dump -U postgres web_dev > backup.sql

# Restore from backup
docker-compose exec -T web-db psql -U postgres web_dev < backup.sql

# Backup with custom format (recommended for large databases)
docker-compose exec web-db pg_dump -U postgres -Fc web_dev > backup.dump

# Restore from custom format
docker-compose exec -T web-db pg_restore -U postgres -d web_dev backup.dump
```

## API Endpoints

### Health Check

- **GET** `/ping`
  - Returns application status and configuration
  - Response:
    ```json
    {
      "ping": "pong!",
      "environment": "dev",
      "testing": false
    }
    ```

## Testing

The project structure is set up to support Test-Driven Development with separate test database configuration. You can add tests in a `tests/` directory and run them inside the container:

```bash
# Execute tests (when test files are added)
docker-compose exec web python -m pytest

# Run tests with coverage
docker-compose exec web python -m pytest --cov=app

# Run specific test file
docker-compose exec web python -m pytest tests/test_example.py
```

The `DATABASE_TEST_URL` environment variable ensures tests use a separate database (`web_test`) to avoid conflicts with development data.

## Production Deployment

For production deployment, consider:

1. Using a production WSGI server configuration
2. Setting appropriate environment variables
3. Implementing proper logging
4. Adding health checks
5. Using multi-stage Docker builds for smaller images
6. Implementing proper secrets management

## Troubleshooting

### Container Won't Start

1. Check if port 8004 is already in use:

   ```bash
   lsof -i :8004
   ```

2. Check Docker logs:
   ```bash
   docker-compose logs web
   docker-compose logs web-db
   ```

### Database Connection Issues

1. Ensure PostgreSQL is running:

   ```bash
   docker-compose ps
   ```

2. Check database logs:

   ```bash
   docker-compose logs web-db
   ```

3. Verify database connectivity:
   ```bash
   docker-compose exec web-db pg_isready -U postgres
   ```

### Migration Issues

1. Reset migrations (⚠️ **This will delete all data**):

   ```bash
   docker-compose exec web aerich init-db
   ```

2. Check migration status:
   ```bash
   docker-compose exec web aerich history
   ```

### Permission Issues

If you encounter permission issues with volume mounts:

```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER ./project
```

### Clean Reset

To completely reset the environment including database:

```bash
# Remove everything and start fresh
docker-compose down -v --rmi all
docker-compose up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
