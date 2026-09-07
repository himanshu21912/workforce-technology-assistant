#!/bin/sh

set -eu

echo "Waiting for PostgreSQL to become available..."

python - <<'PY'
import asyncio
import os

import asyncpg


async def wait_for_postgres() -> None:
    maximum_attempts = 30
    delay_seconds = 2

    for attempt in range(1, maximum_attempts + 1):
        try:
            connection = await asyncpg.connect(
                host=os.environ["POSTGRES_HOST"],
                port=int(os.environ.get("POSTGRES_PORT", "5432")),
                database=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                timeout=5,
            )

            await connection.execute("SELECT 1")
            await connection.close()

            print("PostgreSQL is available.")
            return

        except Exception as exception:
            print(
                f"PostgreSQL connection attempt "
                f"{attempt}/{maximum_attempts} failed: "
                f"{type(exception).__name__}"
            )

            if attempt < maximum_attempts:
                await asyncio.sleep(delay_seconds)

    raise RuntimeError(
        "PostgreSQL did not become available within the expected time."
    )


asyncio.run(wait_for_postgres())
PY

echo "Applying database migrations..."
alembic upgrade head

if [ "${SEED_DATABASE:-true}" = "true" ]; then
    echo "Seeding development data..."
    python -m scripts.seed_database
else
    echo "Database seeding is disabled."
fi

echo "Starting FastAPI application..."

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000
