from fastapi import APIRouter

users_router = APIRouter()

users_router.include_router(users_router,tags=["users模块"])
