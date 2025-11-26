# FastAPI TDD Docker Project

[![CI/CD Pipeline](https://github.com/pedrojunqueira/fastapi-tdd-docker/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/pedrojunqueira/fastapi-tdd-docker/actions)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![UV Package Manager](https://img.shields.io/badge/package%20manager-uv-blue)](https://github.com/astral-sh/uv)

A FastAPI application with PostgreSQL database, containerized with Docker and orchestrated with Docker Compose, designed for Test-Driven Development (TDD) workflows using Tortoise ORM for async database operations.

## 🚀 Latest Updates

**Azure AD Authentication & Authorization**: This project now includes enterprise-grade authentication using Azure Entra ID (formerly Azure AD):

- ✅ **OAuth2 Authorization Code Flow with PKCE** via Swagger UI
- ✅ **Role-based access control** with Admin, Writer, and Reader roles
- ✅ **Azure App Roles integration** - roles defined in Azure, enforced in app
- ✅ **Automatic user provisioning** - users created on first login
- ✅ **Role sync** - roles updated from Azure token on each login

**Azure Deployment Ready**: This project includes full Azure deployment support using Azure Developer CLI (azd):

- ✅ **One-command deployment** to Azure Container Apps
- ✅ **Automatic database migrations** in Azure environment
- ✅ **Cost-effective containerized PostgreSQL** instead of managed database
- ✅ **Smart entrypoint script** that handles first-time setup and subsequent migrations
- ✅ **Production-ready** with monitoring and logging

Deploy to Azure in minutes with: `azd up`

## Project Structure

```
fastapi-tdd-docker/
├── .github/                    # GitHub Actions CI/CD workflows
│   └── workflows/             # GitHub Actions workflow files
│       ├── ci-cd.yml         # Main CI/CD pipeline (test, lint, deploy)
│       └── pr-validation.yml # Pull request validation workflow
├── docker-compose.yml          # Docker Compose configuration
├── AZURE_AUTH_GUIDE.md        # Azure AD authentication setup guide
├── AZURE_ROLES_SETUP.md       # Azure AD roles configuration guide
├── scripts/                    # Development and utility scripts
│   ├── lint.sh               # Ruff linting and formatting script
│   └── setup-github-actions.sh # Azure service principal setup helper
├── project/                    # Application source code
│   ├── Dockerfile             # Docker image definition
│   ├── pyproject.toml         # Python project configuration and dependencies (UV-based)
│   ├── uv.lock                # Locked dependency versions for reproducible builds
│   ├── .dockerignore         # Docker ignore patterns
│   ├── entrypoint.sh         # Container startup script
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
│       ├── main.py          # Main application file with OAuth2 configuration
│       ├── config.py        # Configuration settings including Azure AD
│       ├── auth.py          # Authentication and authorization logic
│       ├── azure.py         # Azure AD scheme initialization
│       ├── db.py            # Tortoise ORM configuration
│       ├── api/             # API routes and endpoints
│       │   ├── __init__.py
│       │   ├── ping.py      # Health check endpoint
│       │   ├── summaries.py # Summaries CRUD endpoints (role-protected)
│       │   └── crud.py      # Database operations
│       └── models/          # Data models
│           ├── __init__.py
│           ├── pydantic.py  # Pydantic schemas for API
│           └── tortoise.py  # Tortoise ORM models (User, TextSummary)
└── README.md                # This file
```

## Features

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Azure AD Authentication**: Enterprise-grade OAuth2 authentication using Azure Entra ID (formerly Azure AD)
- **Role-Based Access Control**: Admin, Writer, and Reader roles with Azure App Roles integration
- **OAuth2 PKCE Flow**: Secure authentication flow in Swagger UI with PKCE support
- **UV Package Manager**: Ultra-fast Python package installation and dependency resolution (10-100x faster than pip)
- **Modular API Structure**: Organized with APIRouter for scalable endpoint management
- **CRUD Operations**: Full Create, Read, Update, Delete operations for summaries
- **PostgreSQL**: Robust relational database with async support
- **Tortoise ORM**: Async ORM inspired by Django ORM for FastAPI
- **Pydantic Schemas**: Type validation and serialization for API requests/responses
- **Database Migrations**: Automated schema management with Aerich
- **Azure Deployment**: One-command deployment to Azure using Azure Developer CLI (azd)
- **Automatic Migration Handling**: Smart entrypoint script that automatically applies database migrations in Azure
- **Containerized Database**: Cost-effective PostgreSQL container deployment in Azure Container Apps
- **Advanced Testing**: Pytest with fixtures, separate test database, and comprehensive code coverage reporting
- **Docker Optimization**: Multi-layer caching with UV for faster container builds
- **Docker Compose**: Multi-container orchestration for local development
- **Environment Configuration**: Configurable settings using Pydantic Settings
- **Hot Reload**: Automatic code reloading during development
- **Python 3.13**: Latest Python version with slim base image and compiled bytecode optimization

## Technology Stack

- **Backend**: FastAPI (Python 3.13)
- **Authentication**: Azure Entra ID (Azure AD) with fastapi-azure-auth library
- **Authorization**: Role-based access control with Azure App Roles
- **Package Manager**: UV (ultra-fast Python package installer and resolver)
- **Database**: PostgreSQL 17
- **ORM**: Tortoise ORM with async support
- **Migration Tool**: Aerich
- **Testing**: Pytest with HTTPX test client and pytest-cov for coverage
- **Containerization**: Docker & Docker Compose
- **Database Driver**: asyncpg

## UV Package Manager

This project uses [UV](https://docs.astral.sh/uv/) instead of pip for Python package management, providing significant performance improvements:

### Benefits of UV

- **Speed**: 10-100x faster than pip for package installation and dependency resolution
- **Reliability**: Built in Rust with robust dependency resolution algorithm
- **Compatibility**: Drop-in replacement for pip with familiar commands
- **Docker Optimization**: Built-in caching and multi-stage builds support
- **Lock Files**: Deterministic builds with `uv.lock` files

### UV vs pip Comparison

- **Installation**: UV installs packages ~10x faster than pip
- **Dependency Resolution**: UV resolves complex dependencies much more efficiently
- **Docker Builds**: Better layer caching and parallel installation
- **Lock Files**: Built-in support for reproducible environments

### Project Configuration

Dependencies are managed in `pyproject.toml`:

```toml
[project]
dependencies = [
    "fastapi==0.115.12",
    "uvicorn[standard]==0.34.1",  # Includes performance extras for production
    "gunicorn==22.0.0",           # WSGI server for production
    # ... other dependencies
]

[project.optional-dependencies]
test = ["pytest", "pytest-cov"]
dev = ["isort"]
```

### Production vs Development

- **Development**: Uses `uv run uvicorn` with `--reload` for hot reloading
- **Production**: Uses `uv run gunicorn` with Uvicorn workers for better performance
- **Uvicorn Standard**: Includes `uvloop`, `httptools`, `watchfiles`, and `websockets` for production optimization

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

### Local Development

Make sure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or higher)

### Azure Deployment

For deploying to Azure, you'll also need:

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Azure Developer CLI (azd)](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
- An active Azure subscription

## Quick Start

### 1. Clone the Repository

```bash
git clone git@github.com:pedrojunqueira/fastapi-tdd-docker.git
cd fastapi-tdd-docker
```

### 2. Build and Start the Application Locally

```bash
# Build the Docker image and start the application
docker-compose up --build -d
```

### 3. Initialize the Database

After the containers are running, you need to apply database migrations:

```bash
# Apply database migrations to create tables
docker-compose exec web aerich upgrade
```

This creates the necessary database tables for the application to function properly.

### 4. Access the Application

Once the container is running, you can access:

- **API Endpoint**: http://localhost:8004/ping
- **Interactive API Documentation**: http://localhost:8004/docs
- **Alternative API Documentation**: http://localhost:8004/redoc

## Services

The application consists of two main services:

- **web**: FastAPI application server
- **web-db**: PostgreSQL database server

## Data Persistence

The application uses Docker volumes to persist PostgreSQL data across container restarts. This ensures your database data survives when you stop and restart containers.

### Volume Configuration

The `web-db` service is configured with a named volume:

```yaml
services:
  web-db:
    # ... other configuration
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Why Use Volumes?

- **Data Persistence**: Your database data survives `docker-compose down`
- **Development Workflow**: No need to recreate test data after restarts
- **Backup/Restore**: Easy to manage with Docker commands

### Volume Management Commands

```bash
# List all volumes
docker volume ls

# Inspect volume details
docker volume inspect fastapi-tdd-docker_postgres_data

# Create a backup of the volume
docker run --rm -v fastapi-tdd-docker_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore from backup
docker run --rm -v fastapi-tdd-docker_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data

# Remove volume (WARNING: This deletes all data!)
docker volume rm fastapi-tdd-docker_postgres_data

# Remove all unused volumes
docker volume prune
```

⚠️ **Important**: Removing volumes will permanently delete all database data. Always backup important data before volume operations.

### Starting Fresh (Clean Slate)

If you want to completely reset your development environment and start with a clean database:

```bash
# Method 1: Stop containers and remove volumes in one command
docker-compose down -v

# Step 2: Start fresh
docker-compose up -d

# Step 3: Apply migrations to recreate tables
docker-compose exec web aerich upgrade
```

**Alternative method (manual volume removal):**

```bash
# Step 1: Stop and remove all containers
docker-compose down

# Step 2: Remove the PostgreSQL volume (deletes all data)
docker volume rm fastapi-tdd-docker_postgres_data

# Step 3: Start fresh
docker-compose up -d

# Step 4: Apply migrations to recreate tables
docker-compose exec web aerich upgrade
```

**One-liner for complete reset:**

```bash
docker-compose down -v && docker-compose up -d && docker-compose exec web aerich upgrade
```

**Use cases for starting fresh:**

- Testing migration scripts
- Cleaning up development data
- Resolving database corruption issues
- Starting with a known clean state

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

1. Add new packages to `project/pyproject.toml`
2. Update the lockfile: `cd project && uv lock`
3. Rebuild the container:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Code Quality with Ruff

This project uses [Ruff](https://docs.astral.sh/ruff/) for fast Python linting and formatting. Ruff is configured in `project/pyproject.toml`.

#### Ruff Configuration

The ruff configuration includes:

- **Linting**: Multiple rule sets including pycodestyle, Pyflakes, pyupgrade, flake8-bugbear, and more
- **Formatting**: Black-compatible code formatting with 88-character line length
- **Import Sorting**: Replaces isort functionality with better performance
- **Type Checking**: Automated import and type annotation improvements
- **Security**: flake8-bandit rules for security vulnerability detection

#### Using Ruff

**Recommended: Use the provided shell script:**

```bash
# Quick commands using the provided script
./scripts/lint.sh check        # Check code quality only
./scripts/lint.sh fix          # Fix linting issues automatically
./scripts/lint.sh format       # Format code (like Black)
./scripts/lint.sh all          # Fix linting + format (recommended for development)
./scripts/lint.sh diff         # Show what changes would be made (dry run)

# Show help
./scripts/lint.sh help
```

**Manual commands (if you prefer direct uv/ruff usage):**

```bash
# Check code quality (linting)
docker-compose exec web uv run ruff check app/ tests/

# Check with auto-fix suggestions
docker-compose exec web uv run ruff check app/ tests/ --fix

# Format code (auto-fix formatting issues)
docker-compose exec web uv run ruff format app/ tests/

# Show what would be changed without applying
docker-compose exec web uv run ruff check app/ --diff
docker-compose exec web uv run ruff format app/ --diff

# Target specific files
docker-compose exec web uv run ruff check app/main.py
docker-compose exec web uv run ruff format app/api/
```

#### Ruff vs Other Tools

Ruff replaces and combines multiple tools:

- **Replaces**: flake8, isort, pyupgrade, autoflake, and parts of black
- **Performance**: 10-100x faster than traditional Python linters
- **Compatibility**: Uses the same configuration format and rules as existing tools
- **Integration**: Built-in VS Code extension support

#### Pre-commit Integration (Optional)

You can also set up ruff to run automatically before commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
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

### Authentication

This application uses **Azure Entra ID (Azure AD)** for enterprise-grade OAuth2 authentication with role-based access control. All endpoints except `/ping` require authentication.

#### Azure AD Configuration

The application requires two Azure AD app registrations:

1. **Backend API App** (`auth-fastapi-tdd`): Defines the API and its app roles
2. **OpenAPI Client App**: Enables OAuth2 flow in Swagger UI

See [AZURE_AUTH_GUIDE.md](AZURE_AUTH_GUIDE.md) for complete setup instructions.

#### Authentication in Swagger UI

1. **Open Swagger UI**: http://localhost:8004/docs
2. **Click "Authorize"** button (green lock icon in top-right)
3. **Check the scope checkbox** (`api://.../.default` or `user_impersonation`)
4. **Click "Authorize"** - you'll be redirected to Microsoft login
5. **Sign in** with your Azure AD credentials
6. **Grant consent** if prompted
7. You're now authenticated and can use the protected endpoints

#### Role-Based Access Control

The application uses Azure AD App Roles for authorization:

| Role       | GET (Read)       | POST (Create) | PUT (Update) | DELETE      |
| ---------- | ---------------- | ------------- | ------------ | ----------- |
| **Admin**  | ✅ All summaries | ✅            | ✅ Any       | ✅ Any      |
| **Writer** | ✅ Own only      | ✅            | ✅ Own only  | ✅ Own only |
| **Reader** | ✅ Own only      | ❌ 403        | ❌ 403       | ❌ 403      |

#### Setting Up Roles in Azure

1. Add app roles (Admin, Writer, Reader) to your Backend API app registration
2. Assign users to roles via Enterprise Applications → Users and groups

See [AZURE_ROLES_SETUP.md](AZURE_ROLES_SETUP.md) for detailed step-by-step instructions.

#### Environment Variables for Azure AD

Configure these in `docker-compose.yml`:

```yaml
environment:
  - TENANT_ID=your-azure-tenant-id
  - APP_CLIENT_ID=your-backend-api-client-id
  - OPENAPI_CLIENT_ID=your-openapi-client-id
```

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

The project is set up for comprehensive Test-Driven Development with pytest, including test fixtures, separate test database configuration, and **code coverage reporting** with interactive HTML reports.

### Key Testing Features

- **pytest**: Modern Python testing framework with fixtures and plugins
- **Test Database Isolation**: Separate `web_test` database for clean testing
- **Code Coverage**: Built-in coverage tracking with `pytest-cov` (currently ~90% coverage)
- **Interactive HTML Reports**: Detailed line-by-line coverage analysis
- **Async Testing**: Full support for testing async FastAPI endpoints
- **Test Fixtures**: Reusable test components and database setup

### Test Structure

- `tests/conftest.py`: Pytest configuration and shared fixtures
- `tests/test_ping.py`: Example test for the ping endpoint
- `tests/test_summaries.py`: CRUD operations testing
- Separate test database (`web_test`) for isolated testing
- `htmlcov/`: Generated HTML coverage reports (after running coverage)

### Pytest Commands

**Note**: If test dependencies aren't available in the container, install them first:

```bash
docker compose exec web uv sync --extra test --extra dev
```

#### Basic Test Execution

```bash
# Normal run - execute all tests
docker compose exec web uv run python -m pytest

# Run with verbose output (detailed test names and results)
docker compose exec web uv run python -m pytest -v

# Disable warnings during test execution
docker compose exec web uv run python -m pytest -p no:warnings

# Run with output capture disabled (see print statements)
docker compose exec web uv run python -m pytest -s
```

#### Selective Test Execution

```bash
# Run specific test file
docker compose exec web uv run python -m pytest tests/test_ping.py

# Run specific test function
docker compose exec web uv run python -m pytest tests/test_ping.py::test_ping

# Run tests matching a pattern (supports complex expressions)
docker compose exec web uv run python -m pytest -k "ping"
docker compose exec web uv run python -m pytest -k "summary and not test_read_summary"

# Run only the last failed tests
docker compose exec web uv run python -m pytest --lf
```

#### Failure Handling

```bash
# Stop the test session after the first failure
docker compose exec web uv run python -m pytest -x

# Stop the test run after specific number of failures
docker compose exec web uv run python -m pytest --maxfail=2

# Enter Python debugger (PDB) after first failure then end session
docker compose exec web uv run python -m pytest -x --pdb

# Show local variables in tracebacks for better debugging
docker compose exec web uv run python -m pytest -l
```

#### Performance and Analysis

```bash
# List the slowest tests (adjust number as needed)
docker compose exec web uv run python -m pytest --durations=2
docker compose exec web uv run python -m pytest --durations=10

# Run tests in parallel (if pytest-xdist is installed)
docker compose exec web uv run python -m pytest -n auto
```

#### Coverage Reports

The project includes comprehensive code coverage tracking using `pytest-cov` (coverage.py integration for pytest). Coverage reports help identify untested code and maintain code quality.

```bash
# Run tests with basic coverage report in terminal
docker compose exec web uv run python -m pytest --cov=app

# Generate detailed HTML coverage report (recommended)
docker compose exec web uv run python -m pytest --cov=app --cov-report=html

# Show missing lines in terminal coverage report
docker compose exec web uv run python -m pytest --cov=app --cov-report=term-missing

# Generate multiple report formats simultaneously
docker compose exec web uv run python -m pytest --cov=app --cov-report=html --cov-report=term-missing

# Combine coverage with other pytest options
docker compose exec web uv run python -m pytest --cov=app --cov-report=html -v -s

# Set minimum coverage threshold (fails if below threshold)
docker compose exec web uv run python -m pytest --cov=app --cov-fail-under=85

# Include coverage for test files themselves
docker compose exec web uv run python -m pytest --cov=app --cov=tests --cov-report=html
```

#### Interactive HTML Coverage Reports

When you run tests with `--cov-report=html`, an interactive HTML report is generated in the `htmlcov/` directory:

```bash
# Generate HTML coverage report
docker compose exec web uv run python -m pytest --cov=app --cov-report=html

# View the report (copy to your host system and open in browser)
# The main report file is: project/htmlcov/index.html
```

**HTML Report Features:**

- **Overall Coverage**: Shows total coverage percentage (currently ~90%)
- **File-by-File Breakdown**: Detailed coverage for each Python file
- **Line-by-Line Analysis**: Click on any file to see exactly which lines are covered/missed
- **Interactive Filtering**: Filter files by coverage percentage or name
- **Missing Coverage Highlights**: Red highlighting shows uncovered lines
- **Branch Coverage**: Shows if all conditional branches are tested

**Accessing HTML Reports:**

1. After running tests with HTML coverage, the report is saved to `project/htmlcov/index.html`
2. Copy the entire `htmlcov/` folder to your local machine to view in a browser
3. Open `index.html` in your web browser for the interactive report

#### Coverage Configuration

The coverage configuration is managed through pytest command-line options. Common configurations:

```bash
# Focus coverage on specific modules/packages
docker compose exec web uv run python -m pytest --cov=app.api --cov-report=html

# Exclude specific files or directories from coverage
docker compose exec web uv run python -m pytest --cov=app --cov-report=html --ignore=tests/

# Include branch coverage (measures if all code paths are tested)
docker compose exec web uv run python -m pytest --cov=app --cov-branch --cov-report=html
```

#### Coverage Best Practices

- **Target 80-90% Coverage**: Aim for high coverage but don't obsess over 100%
- **Focus on Critical Paths**: Ensure business logic and API endpoints are well tested
- **Review HTML Reports**: Use the interactive HTML reports to identify missed edge cases
- **Branch Coverage**: Consider using `--cov-branch` for more thorough testing
- **Exclude Non-Testable Code**: Some code (like `if __name__ == "__main__"`) should be excluded

#### Coverage Files

Coverage generates several files during execution:

- `htmlcov/`: Directory containing interactive HTML reports
- `.coverage`: Raw coverage data (binary format)
- Coverage files are typically added to `.gitignore` to avoid committing large reports

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

## Azure Deployment with azd

This project is configured for deployment to Azure using the Azure Developer CLI (azd). The infrastructure is defined using Bicep templates and will create the following Azure resources:

### Azure Resources Created

- **Azure Container Apps**: Hosts both your FastAPI application and PostgreSQL database with auto-scaling
- **Azure Container Registry**: Stores your Docker images
- **PostgreSQL Container**: Containerized PostgreSQL database (same as local development)
- **Azure Log Analytics**: Centralized logging and monitoring
- **Azure Application Insights**: Application performance monitoring

### Infrastructure Files Structure

```
infra/
├── main.bicep                    # Main infrastructure template
├── main.parameters.json          # Environment-specific parameters
├── abbreviations.json            # Azure resource naming conventions
├── app/
│   ├── web.bicep                 # FastAPI Container App configuration
│   └── database-container.bicep  # PostgreSQL Container App setup
└── core/
    ├── host/
    │   ├── container-apps.bicep  # Container Apps Environment
    │   └── container-app.bicep   # Individual Container App
    └── monitor/
        └── monitoring.bicep      # Logging and monitoring
```

### How Azure Developer CLI (azd) Works

1. **`azure.yaml`**: Defines your application and how azd should handle it
2. **`infra/`**: Contains Bicep templates that define your Azure infrastructure
3. **Deployment Process**:
   - azd provisions Azure resources using Bicep
   - Builds and pushes your Docker images to Azure Container Registry
   - Deploys both FastAPI and PostgreSQL containers to Azure Container Apps
   - Automatically handles database migrations via the updated entrypoint script

### Database Architecture: Containerized PostgreSQL

This project uses a **containerized PostgreSQL database** instead of Azure Database for PostgreSQL, providing several advantages:

#### Benefits:

- **Cost Effective**: Significantly cheaper than managed PostgreSQL service
- **Consistency**: Identical database setup between local development and production
- **Simplicity**: No complex networking or firewall configuration required
- **Control**: Full control over PostgreSQL version and configuration
- **Docker Compatibility**: Uses the same PostgreSQL Docker image as local development

#### How It Works:

1. **Two Container Apps**: Your application runs as two separate container apps:
   - `web`: Your FastAPI application
   - `database`: PostgreSQL database container
2. **Internal Communication**: Containers communicate internally within the Container Apps environment
3. **Persistent Storage**: Database data persists across container restarts
4. **Secure Credentials**: Uses generated unique passwords per deployment (not hardcoded credentials)

#### Database URL:

```
postgresql://postgres:{generated-password}@{database-container-name}:5432/web_production
```

**Security Note**: The database password is automatically generated using Azure's `uniqueString()` function based on your subscription ID and environment name, ensuring each deployment has a unique, unpredictable password.

### Database Migrations in Azure

The application automatically handles database migrations during deployment:

#### Migration Strategy:

- **First-time Deployment**: When deploying to a fresh Azure environment, the `entrypoint.sh` script automatically runs `aerich upgrade` to apply all existing migrations
- **Subsequent Deployments**: New migrations are automatically applied during container startup
- **Migration Files**: All migration files in `migrations/models/` are included in the Docker image

#### How It Works:

1. Container starts and waits for PostgreSQL database to be ready
2. In production environment (`ENVIRONMENT=production`), the script runs:
   ```bash
   aerich upgrade
   ```
3. This applies all migrations from the `migrations/models/` directory to the Azure PostgreSQL database
4. Application starts normally after migrations complete

#### Migration Logs:

You can monitor migration execution in the container logs using Azure CLI:

```bash
# First, find your container app names
az containerapp list --resource-group rg-fastapi-tdd-dev --output table

# View logs from your web container app (replace with your actual container app name)
az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --follow

# Or get recent logs (last 50 lines)
az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --tail 50

# Look for: "Running database migrations..." and "Success upgrading to..."
```

### Deployment Commands

#### First-time Setup

```bash
# Initialize azd for your project (already done)
azd init

# Login to Azure
azd auth login

# Set target location to Australia East (optional)
azd env set AZURE_LOCATION australiaeast

# Provision Azure resources and deploy application
azd up
```

#### Development Workflow

```bash
# Deploy only code changes (faster than full provision)
azd deploy

# Provision infrastructure changes
azd provision

# Full deployment (provision + deploy)
azd up

# View deployed application
azd show

# View application logs (including migration logs)
az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --follow

# Clean up all Azure resources
azd down
```

#### Environment Management

```bash
# Create a new environment (e.g., staging, production)
azd env new staging

# Switch between environments
azd env select production

# List all environments
azd env list

# View current environment variables
azd env get-values
```

### Step-by-Step Deployment Guide

1. **Install Prerequisites**:

   ```bash
   # Install Azure CLI (macOS)
   brew install azure-cli

   # Install Azure Developer CLI (macOS)
   brew tap azure/azd && brew install azd
   ```

2. **Login to Azure**:

   ```bash
   azd auth login
   ```

3. **Deploy to Azure**:

   ```bash
   # Full deployment (first time)
   azd up

   # Or step by step:
   azd provision  # Create Azure resources
   azd deploy     # Deploy application
   ```

### Testing Your Deployment

After deployment, test your API endpoints:

```bash
# Get the application URL
azd show

# Test health endpoint
curl https://your-app-url.azurecontainerapps.io/ping

# Test summaries API
curl https://your-app-url.azurecontainerapps.io/summaries/

# Create a new summary
curl -X POST https://your-app-url.azurecontainerapps.io/summaries/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

### Environment Configuration

The Azure deployment uses these environment variables:

- `ENVIRONMENT=production`
- `TESTING=0`
- `DATABASE_URL`: Automatically configured to point to the PostgreSQL container
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Auto-configured for monitoring

### Monitoring Your Application

After deployment, you can monitor your application through:

- **Container Apps Logs**: View via Azure CLI commands or Azure Portal
- **Application Insights**: Performance metrics and logs
- **Azure Portal**: Full resource management interface

## Production Deployment (Legacy Notes)

For traditional production deployment approaches, consider:

1. Using a production WSGI server configuration
2. Setting appropriate environment variables
3. Implementing proper logging
4. Adding health checks
5. Using multi-stage Docker builds for smaller images
6. Implementing proper secrets management

## Troubleshooting

### Local Development Issues

#### Container Won't Start

1. Check if port 8004 is already in use:

   ```bash
   lsof -i :8004
   ```

2. Check Docker logs:
   ```bash
   docker-compose logs web
   docker-compose logs web-db
   ```

#### Database Connection Issues

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

#### Migration Issues

1. Reset migrations (⚠️ **This will delete all data**):

   ```bash
   docker-compose exec web aerich init-db
   ```

2. Check migration status:
   ```bash
   docker-compose exec web aerich history
   ```

#### Permission Issues

If you encounter permission issues with volume mounts:

```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER ./project
```

#### Clean Reset

To completely reset the environment including database:

```bash
# Remove everything and start fresh
docker-compose down -v --rmi all
docker-compose up --build
```

### Azure Deployment Issues

#### azd Authentication Problems

1. Login to Azure:

   ```bash
   azd auth login
   ```

2. Check current subscription:

   ```bash
   az account show
   ```

3. Set correct subscription if needed:
   ```bash
   az account set --subscription "your-subscription-id"
   ```

#### Deployment Failures

1. Check container logs for detailed error information:

   ```bash
   az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --tail 100
   ```

2. View specific container logs:

   ```bash
   az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --follow false --tail 50
   ```

3. Redeploy with clean state:
   ```bash
   azd down  # Remove all resources
   azd up    # Recreate everything
   ```

#### Database Migration Issues in Azure

1. Check if migrations ran successfully in container logs:

   ```bash
   az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --follow
   # Look for: "Running database migrations..." and "Success upgrading to..."
   ```

2. If migrations failed, check the specific error:

   ```bash
   az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --follow false | grep -A 10 -B 10 "aerich"
   ```

3. Force redeploy to retry migrations:
   ```bash
   azd deploy
   ```

#### API Endpoints Not Working

1. Test the health endpoint first:

   ```bash
   curl https://your-app-url.azurecontainerapps.io/ping
   ```

2. Check if the database connection is working:

   ```bash
   curl https://your-app-url.azurecontainerapps.io/summaries/
   # Should return [] for empty database
   ```

3. If getting "Internal Server Error", check container logs for Python tracebacks:
   ```bash
   az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --tail 50 | grep -A 20 "ERROR"
   ```

#### Container Apps Not Starting

1. Check container app status:

   ```bash
   az containerapp show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --query "properties.runningStatus"
   ```

2. Check if database container is running:

   ```bash
   az containerapp show --name ca-db-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --query "properties.runningStatus"
   ```

3. Restart containers if needed:
   ```bash
   az containerapp revision restart --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev
   ```

#### Resource Limits or Scaling Issues

1. Check current resource allocation:

   ```bash
   az containerapp show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --query "properties.template.containers[0].resources"
   ```

2. Update Bicep templates in `infra/` to adjust CPU/memory if needed

#### Networking Issues

1. Verify container apps can communicate:

   ```bash
   # Check if database container is accessible from web container
   az containerapp logs show --name ca-web-mfhsztqp2zg3m --resource-group rg-fastapi-tdd-dev --tail 50 | grep "database connection"
   ```

2. Ensure containers are in the same Container Apps Environment

#### Common Solutions

- **Migrations not running**: Ensure `ENVIRONMENT=production` is set in the container environment
- **Database connection timeout**: Check if both containers are in the same Container Apps Environment
- **Image build failures**: Verify Dockerfile.prod and ensure all dependencies are properly specified
- **Port issues**: Ensure container is exposing port 8000 (not 8004 like local development)

## CI/CD Pipeline with GitHub Actions

This project includes a comprehensive CI/CD pipeline that automatically tests, validates, and deploys your FastAPI application to Azure.

### Pipeline Overview

The CI/CD pipeline consists of multiple workflows:

#### 1. Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

Triggers on pushes to `master` branch and runs:

**Testing & Coverage:**

- Sets up PostgreSQL test database
- Runs all tests with pytest
- Generates coverage reports (minimum 80% required)
- Uploads coverage to Codecov
- Archives HTML coverage reports as artifacts

**Code Quality:**

- Linting with Ruff (all configured rule sets)
- Code formatting validation with Ruff
- Security scanning with Ruff security rules

**Build Validation:**

- Tests Docker image builds (development and production)
- Uses GitHub Actions cache for faster builds

**Azure Deployment** (only on `master` pushes):

- Authenticates with Azure using service principal
- Deploys using `azd up` command
- Tests deployed application endpoints
- Creates deployment summary with links

#### 2. Pull Request Validation (`.github/workflows/pr-validation.yml`)

Runs the same quality checks on pull requests but skips deployment:

- All tests and coverage checks
- Code quality validation
- Security scanning
- Docker build validation
- Automatic PR comments on failures

### Required GitHub Secrets

To set up the CI/CD pipeline, add these secrets to your GitHub repository:

#### Azure Authentication (Required for deployment)

1. **Create Azure Service Principal:**

   ```bash
   # Login to Azure
   az login

   # Create service principal with Contributor role
   az ad sp create-for-rbac \
     --name "github-actions-fastapi-tdd" \
     --role contributor \
     --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID> \
     --output json

   # Add User Access Administrator role (required for azd deployments)
   az role assignment create \
     --assignee <CLIENT_ID_FROM_ABOVE> \
     --role "User Access Administrator" \
     --scope /subscriptions/<YOUR_SUBSCRIPTION_ID>
   ```

   > **Note**: Both Contributor and User Access Administrator roles are required for successful Azure deployments with azd.

2. **Add GitHub Secrets:**
   - `AZURE_CLIENT_ID` - Service principal client ID
   - `AZURE_CLIENT_SECRET` - Service principal client secret
   - `AZURE_TENANT_ID` - Your Azure tenant ID
   - `AZURE_SUBSCRIPTION_ID` - Your Azure subscription ID

#### Optional Secrets

- `CODECOV_TOKEN` - For coverage reporting (get from [codecov.io](https://codecov.io))

### GitHub Secrets Setup

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each secret above

### Pipeline Features

**🚀 **Performance Optimizations:\*\*

- UV package manager for ultra-fast dependency installation
- Docker layer caching with GitHub Actions cache
- Parallel job execution where possible
- Smart conditional deployments

**🛡️ **Security & Quality:\*\*

- Comprehensive security scanning with Ruff
- Code coverage enforcement (80% minimum)
- Automated formatting and linting validation

**📊 **Monitoring & Reporting:\*\*

- Coverage reports with HTML artifacts
- Deployment health checks
- Detailed GitHub Actions summaries
- PR status checks and comments

**🔄 **Azure Integration:\*\*

- Automated deployment to Azure Container Apps
- Environment-specific configurations
- Post-deployment health verification
- Rollback capabilities via Azure portal

### Development Workflow

1. **Create Feature Branch:**

   ```bash
   git checkout -b feature/new-feature
   ```

2. **Development with Quality Checks:**

   ```bash
   # Run tests locally
   docker-compose exec web uv run python -m pytest --cov=app --cov-report=html

   # Check code quality
   ./scripts/lint.sh all

   # Test Docker build
   docker-compose up --build
   ```

3. **Create Pull Request:**

   - Push to feature branch
   - Create PR against `master`
   - PR validation workflow runs automatically
   - Address any failing checks

4. **Merge and Deploy:**
   - Merge PR to `master`
   - Main CI/CD pipeline runs automatically
   - Application deploys to Azure if all checks pass

### Pipeline Status and Monitoring

**Badge Examples (add to your README):**

```markdown
![CI/CD](https://github.com/pedrojunqueira/fastapi-tdd-docker/workflows/CI/CD%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/pedrojunqueira/fastapi-tdd-docker/branch/master/graph/badge.svg)
```

**View Pipeline Results:**

- **Actions Tab:** See all workflow runs and logs
- **Deployments:** View deployment history and status
- **Security Tab:** Review security alerts and dependency updates
- **Codecov:** Detailed coverage reports and trends

### Troubleshooting CI/CD

**Common Issues:**

1. **Azure Authentication Failures:**

   ```bash
   # Verify service principal permissions
   az role assignment list --assignee <CLIENT_ID>
   ```

2. **Test Failures:**

   ```bash
   # Run tests locally with same environment
   docker-compose exec web uv run python -m pytest -v --tb=short
   ```

3. **Coverage Below Threshold:**

   ```bash
   # Generate detailed coverage report
   docker-compose exec web uv run python -m pytest --cov=app --cov-report=html
   # Open project/htmlcov/index.html to see uncovered lines
   ```

4. **Code Quality Failures:**
   ```bash
   # Fix automatically
   ./scripts/lint.sh all
   ```

**Pipeline Optimization:**

- Tests run in ~2-3 minutes with PostgreSQL service
- Code quality checks complete in ~1 minute
- Docker builds leverage caching for faster runs
- Azure deployment typically takes 3-5 minutes

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code quality standards
4. Add tests for new functionality
5. Ensure all local checks pass:
   ```bash
   ./scripts/lint.sh all
   docker-compose exec web uv run python -m pytest --cov=app --cov-fail-under=80
   ```
6. Submit a pull request
7. Wait for CI/CD validation to pass
8. Address any review feedback

## License

This project is licensed under the MIT License - see the LICENSE file for details.
