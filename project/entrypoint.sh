#!/bin/sh

echo "Waiting for postgres..."

# Extract host from DATABASE_URL if available
if [ -n "$DATABASE_URL" ]; then
    # Extract host from postgresql://user:pass@host:port/db format
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [ -z "$DB_PORT" ]; then
        DB_PORT=5432
    fi
    
    echo "Checking database connection to $DB_HOST:$DB_PORT..."
    
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
        echo "Still waiting for database..."
    done
else
    # Fallback for local development
    while ! nc -z web-db 5432; do
        sleep 0.1
    done
fi

echo "PostgreSQL started"

# Run database migrations if in production
if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "prod" ]; then
    echo "Running database migrations..."
    
    # Since migrations are already initialized in the repo, 
    # we just need to apply them to the database
    echo "Applying aerich migrations..."
    uv run aerich upgrade
fi

exec "$@"