import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.commons import migrate
from src.commons.postgres import database
from src.users.users_route import users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await migrate.apply_pending_migrations()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)


app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0")
