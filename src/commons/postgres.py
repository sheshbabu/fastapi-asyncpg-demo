import asyncpg


DATABASE_URL = "postgresql://postgres@localhost/postgres"


class Postgres:
    def __init__(self, database_url: str):
        self.database_url = database_url

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)

    async def disconnect(self):
        self.pool.terminate()


database = Postgres(DATABASE_URL)
