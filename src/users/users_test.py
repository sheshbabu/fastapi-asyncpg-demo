import pytest
from httpx import AsyncClient, ASGITransport
from src.commons.postgres import database
from src.commons import migrate
from src.main import app


@pytest.fixture()
async def setup_database():
    await database.connect()
    async with database.pool.acquire() as connection:
        await connection.execute("CREATE SCHEMA IF NOT EXISTS public;")
    await migrate.apply_pending_migrations()

    yield

    async with database.pool.acquire() as connection:
        await connection.execute("DROP SCHEMA IF EXISTS public CASCADE;")
    await database.disconnect()


@pytest.fixture
async def client_app():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_get_users_returns_empty_list_when_no_users_exist(setup_database, client_app):
    response = await client_app.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_users_returns_users_list_when_users_exist(setup_database, client_app):
    async with database.pool.acquire() as connection:
        await connection.execute("INSERT INTO users (name, email) VALUES ($1, $2)", "Shesh", "sheshbabu@gmail.com")
    response = await client_app.get("/users/")
    assert response.status_code == 200
    assert response.json() == [{"email": "sheshbabu@gmail.com", "name": "Shesh"}]


@pytest.mark.asyncio
async def test_post_users_returns_success_status_when_valid_payload_is_provided(setup_database, client_app):
    payload = {"name": "Shesh", "email": "sheshbabu@gmail.com"}
    response = await client_app.post("/users/", json=payload)
    assert response.status_code == 200
