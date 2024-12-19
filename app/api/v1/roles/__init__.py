from fastapi import APIRouter

roles_router = APIRouter()

roles_router.include_router(roles_router,tags=["roles模块"])
