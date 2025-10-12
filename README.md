# FastAPI TDD Docker Project

A simple FastAPI application containerized with Docker and orchestrated with Docker Compose.

## Project Structure

```
fastapi-tdd-docker/
├── docker-compose.yml          # Docker Compose configuration
├── project/                    # Application source code
│   ├── Dockerfile             # Docker image definition
│   ├── requirements.txt       # Python dependencies
│   ├── .dockerignore         # Docker ignore patterns
│   └── app/                  # FastAPI application
│       ├── __init__.py
│       ├── main.py           # Main application file
│       └── config.py         # Configuration settings
└── README.md                 # This file
```

## Features

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Docker**: Containerized application for consistent development and deployment
- **Docker Compose**: Simple orchestration for local development
- **Environment Configuration**: Configurable settings using Pydantic Settings
- **Hot Reload**: Automatic code reloading during development
- **Python 3.13**: Latest Python version with slim base image

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

## Docker Compose Commands

### Build the Application

```bash
# Build the Docker image
docker-compose build

# Build without using cache
docker-compose build --no-cache
```

### Start the Application

```bash
# Start in foreground (with logs)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start with rebuild
docker-compose up --build
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

These can be modified in the `docker-compose.yml` file under the `environment` section.

### Hot Reload

The application is configured with `--reload` flag and volume mounting, so any changes to the code will automatically restart the server.

### Adding Dependencies

1. Add new packages to `project/requirements.txt`
2. Rebuild the container:
   ```bash
   docker-compose down
   docker-compose up --build
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

The project structure is set up to support Test-Driven Development. You can add tests in a `tests/` directory and run them inside the container:

```bash
# Execute tests (when test files are added)
docker-compose exec web python -m pytest
```

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
   ```

### Permission Issues

If you encounter permission issues with volume mounts:

```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER ./project
```

### Clean Reset

To completely reset the environment:

```bash
# Remove everything and start fresh
docker-compose down --rmi all
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
