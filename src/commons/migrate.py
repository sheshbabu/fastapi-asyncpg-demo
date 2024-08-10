from pathlib import Path
from src.commons.postgres import database

async def create_table():
    query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version     INTEGER   PRIMARY KEY,
            name        TEXT      NOT NULL,
            migrated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """
    async with database.pool.acquire() as connection:
        await connection.execute(query)
        await connection.close()

async def get_pending_migrations():
    # Get all migration files
    migrations = []
    for path in Path('./src/migrations').iterdir():
        if not path.is_file():
            continue
        migration = {}
        migration["name"] = path.name
        migration["content"] = path.read_text()
        migration["version"] = int(path.name.split("_")[0])
        migrations.append(migration)

    # Get all applied versions
    query = "SELECT version from schema_migrations ORDER BY version ASC"
    async with database.pool.acquire() as connection:
        records = await connection.fetch(query)
        applied_versions = [r["version"] for r in records]

    # Filter out applied migrations
    migrations = [m for m in migrations if m["version"] not in applied_versions]

    # Sort migrations by version
    migrations = sorted(migrations, key=lambda m: m['version'])
    return migrations


async def apply_pending_migrations():
    await create_table()
    migrations = await get_pending_migrations()

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            for migration in migrations:
                await connection.execute(migration["content"])
                await connection.execute("INSERT INTO schema_migrations (version, name) VALUES ($1, $2)", migration["version"], migration["name"])