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
    echo "Checking database state..."
    
    # Check if textsummary table exists
    python -c "
import asyncio
import os
from tortoise import Tortoise

async def check_tables():
    await Tortoise.init(
        db_url=os.environ.get('DATABASE_URL'),
        modules={'models': ['app.models.tortoise']},
    )
    
    connection = Tortoise.get_connection('default')
    result = await connection.execute_query(
        \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'textsummary')\"
    )
    table_exists = result[1][0]['exists']
    await Tortoise.close_connections()
    
    if table_exists:
        print('TABLES_EXIST')
    else:
        print('TABLES_MISSING')

asyncio.run(check_tables())
" > /tmp/db_state.txt

    DB_STATE=$(cat /tmp/db_state.txt)
    
    if [ "$DB_STATE" = "TABLES_MISSING" ]; then
        echo "First-time setup: Initializing database with aerich init-db..."
        aerich init-db
    else
        echo "Database exists: Running aerich upgrade..."
        aerich upgrade
    fi
fi

exec "$@"