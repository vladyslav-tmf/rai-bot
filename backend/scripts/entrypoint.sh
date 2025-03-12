#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Function to wait for the database to be ready
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! python -c "
import sys
import asyncio
import asyncpg

async def check_db():
    try:
        conn = await asyncpg.connect(
            database='${POSTGRES_DB}',
            user='${POSTGRES_USER}',
            password='${POSTGRES_PASSWORD}',
            host='${POSTGRES_SERVER}',
            port=${POSTGRES_PORT}
        )
        await conn.close()
        return True
    except Exception:
        return False

if not asyncio.run(check_db()):
    sys.exit(1)
"
    do
        echo "Database is not ready. Waiting..."
        sleep 1
    done
    echo "Database is ready!"
}

echo "Running migrations..."
wait_for_db

# Run migrations
cd /app
alembic upgrade head

echo "Starting the application..."
uvicorn 'backend.app.main:app' --host=0.0.0.0 --port=8000 --reload
