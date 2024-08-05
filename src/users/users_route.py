from typing import Optional, List
from fastapi import APIRouter
from src.users import users_model
from src.users.users_schema import User


users_router = APIRouter(prefix="/users")

# curl http://localhost:8000/users/
@users_router.get("/")
async def get_all_users(limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await users_model.get_all_users(limit, offset)

# curl http://localhost:8000/users/abc@xyz.com
@users_router.get("/{email}")
async def get_user_by_email(email: str):
    return await users_model.get_user_by_email(email)

# curl --header "Content-Type: application/json" --request POST --data '{"name":"abc","email":"abc@xyz.com"}' http://localhost:8000/users/
@users_router.post("/")
async def insert_user(user: User):
    return await users_model.insert_user(user)

# curl --header "Content-Type: application/json" --request POST --data '[{"name":"ijk","email":"ijk@xyz.com"}, {"name":"ijk2","email":"ijk2@xyz.com"}]' http://localhost:8000/users/bulk
@users_router.post("/bulk")
async def bulk_insert_users(users: List[User]):
    return await users_model.bulk_insert_users(users)
