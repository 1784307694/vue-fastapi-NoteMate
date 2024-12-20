from fastapi import APIRouter
from .users import users_router
from .roles import roles_router

v1_router  = APIRouter()

# 后续依赖注入在此进行

v1_router.include_router(users_router, prefix="/users")
v1_router.include_router(roles_router, prefix="/roles")

