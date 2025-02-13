from fastapi import APIRouter

from .users import users_router
from .roles import roles_router
from .apis import apis_router
from .base import base_router
from .menus import menus_router
from .auditlog import auditlog_router   
from .notes import notes_router

from app.core.dependency import DependPermisson

v1_router  = APIRouter()

# 后续依赖注入在此进行
v1_router.include_router(users_router, prefix="/users", dependencies=[DependPermisson])
v1_router.include_router(roles_router, prefix="/roles", dependencies=[DependPermisson])
v1_router.include_router(apis_router, prefix="/apis", dependencies=[DependPermisson])
v1_router.include_router(menus_router, prefix="/menus", dependencies=[DependPermisson])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermisson])
v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(notes_router, prefix="/notes")

__all__ = ["v1_router"]
