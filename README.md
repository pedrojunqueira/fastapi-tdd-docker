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
│   ├── tests/               # Test files
│   │   ├── __init__.py
│   │   ├── conftest.py      # Pytest configuration and fixtures
│   │   └── test_ping.py     # Example test file
│   └── app/                 # FastAPI application
│       ├── __init__.py
│       ├── main.py          # Main application file
│       ├── config.py        # Configuration settings
│       ├── db.py            # Tortoise ORM configuration
│       ├── api/             # API routes and endpoints
│       │   ├── __init__.py
│       │   ├── ping.py      # Health check endpoint
│       │   ├── summaries.py # Summaries CRUD endpoints
│       │   └── crud.py      # Database operations
│       └── models/          # Data models
│           ├── __init__.py
│           ├── pydantic.py  # Pydantic schemas for API
│           └── tortoise.py  # Tortoise ORM models
└── README.md                # This file
```

## Features

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Modular API Structure**: Organized with APIRouter for scalable endpoint management
- **CRUD Operations**: Full Create, Read, Update, Delete operations for summaries
- **PostgreSQL**: Robust relational database with async support
- **Tortoise ORM**: Async ORM inspired by Django ORM for FastAPI
- **Pydantic Schemas**: Type validation and serialization for API requests/responses
- **Database Migrations**: Automated schema management with Aerich
- **Testing**: Pytest with test fixtures and separate test database
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
- **Testing**: Pytest with HTTPX test client
- **Containerization**: Docker & Docker Compose
- **Database Driver**: asyncpg

## Application Architecture

### Modular Structure

The application follows a modular architecture pattern:

- **`app/main.py`**: Application factory and router registration
- **`app/api/`**: API layer with organized routers
  - `ping.py`: Health check endpoints
  - `summaries.py`: Summaries CRUD endpoints
  - `crud.py`: Database operations and business logic
- **`app/models/`**: Data models and schemas
  - `tortoise.py`: Database models using Tortoise ORM
  - `pydantic.py`: API request/response schemas
- **`app/config.py`**: Application configuration management
- **`app/db.py`**: Database connection and initialization

### Data Flow

1. **API Request** → FastAPI Router (`app/api/summaries.py`)
2. **Validation** → Pydantic Schema (`app/models/pydantic.py`)
3. **Business Logic** → CRUD Operations (`app/api/crud.py`)
4. **Data Persistence** → Tortoise ORM Models (`app/models/tortoise.py`)
5. **Database** → PostgreSQL

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

The project includes models for managing text summaries:

**Tortoise ORM Model** (`app/models/tortoise.py`):

```python
class TextSummary(models.Model):
    url = fields.TextField()
    summary = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

# Auto-generated Pydantic model for API responses
SummarySchema = pydantic_model_creator(TextSummary)
```

**Pydantic Schemas** (`app/models/pydantic.py`):

```python
class SummaryPayloadSchema(BaseModel):
    url: str

class SummaryResponseSchema(SummaryPayloadSchema):
    id: int
```

### API Router Structure

The application uses FastAPI's APIRouter for modular endpoint organization:

```python
# app/main.py
app.include_router(ping.router)
app.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
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

### Summaries

The summaries API provides CRUD operations for managing text summaries.

- **POST** `/summaries/`

  - Create a new summary
  - Request body:
    ```json
    {
      "url": "https://example.com/article"
    }
    ```
  - Response (201 Created):
    ```json
    {
      "id": 1,
      "url": "https://example.com/article"
    }
    ```

- **GET** `/summaries/{id}/`
  - Retrieve a specific summary by ID
  - Response (200 OK):
    ```json
    {
      "id": 1,
      "url": "https://example.com/article",
      "summary": "Generated summary text...",
      "created_at": "2025-10-16T10:30:00Z"
    }
    ```
  - Response (404 Not Found):
    ```json
    {
      "detail": "Summary not found"
    }
    ```

### API Documentation

Once the application is running, you can access:

- **Interactive API Documentation (Swagger UI)**: http://localhost:8004/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8004/redoc
- **OpenAPI JSON Schema**: http://localhost:8004/openapi.json

## Testing

The project is set up for Test-Driven Development with pytest, including test fixtures and a separate test database configuration.

### Test Structure

- `tests/conftest.py`: Pytest configuration and shared fixtures
- `tests/test_ping.py`: Example test for the ping endpoint
- Separate test database (`web_test`) for isolated testing

### Pytest Commands

#### Basic Test Execution

```bash
# Normal run - execute all tests
docker compose exec web python -m pytest

# Run with verbose output (detailed test names and results)
docker compose exec web python -m pytest -v

# Disable warnings during test execution
docker compose exec web python -m pytest -p no:warnings

# Run with output capture disabled (see print statements)
docker compose exec web python -m pytest -s
```

#### Selective Test Execution

```bash
# Run specific test file
docker compose exec web python -m pytest tests/test_ping.py

# Run specific test function
docker compose exec web python -m pytest tests/test_ping.py::test_ping

# Run tests matching a pattern (supports complex expressions)
docker compose exec web python -m pytest -k "ping"
docker compose exec web python -m pytest -k "summary and not test_read_summary"

# Run only the last failed tests
docker compose exec web python -m pytest --lf
```

#### Failure Handling

```bash
# Stop the test session after the first failure
docker compose exec web python -m pytest -x

# Stop the test run after specific number of failures
docker compose exec web python -m pytest --maxfail=2

# Enter Python debugger (PDB) after first failure then end session
docker compose exec web python -m pytest -x --pdb

# Show local variables in tracebacks for better debugging
docker compose exec web python -m pytest -l
```

#### Performance and Analysis

```bash
# List the slowest tests (adjust number as needed)
docker compose exec web python -m pytest --durations=2
docker compose exec web python -m pytest --durations=10

# Run tests in parallel (if pytest-xdist is installed)
docker compose exec web python -m pytest -n auto
```

#### Coverage Reports

```bash
# Run tests with coverage report
docker compose exec web python -m pytest --cov=app

# Generate HTML coverage report
docker compose exec web python -m pytest --cov=app --cov-report=html

# Show missing lines in coverage report
docker compose exec web python -m pytest --cov=app --cov-report=term-missing

# Combine coverage with other options
docker compose exec web python -m pytest --cov=app --cov-report=html -v
```

### Test Database Management

```bash
# The test database (web_test) is automatically used during testing
# You can connect to it directly if needed:
docker-compose exec web-db psql -U postgres -d web_test

# Reset test database (if needed)
docker-compose exec web-db psql -U postgres -c "DROP DATABASE IF EXISTS web_test; CREATE DATABASE web_test;"
```

### Writing Tests

Tests use the TestClient from Starlette with dependency overrides for configuration:

```python
def test_ping(test_app):
    response = test_app.get("/ping")
    assert response.status_code == 200
    assert response.json() == {
        "ping": "pong!",
        "environment": "dev",
        "testing": True
    }
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
