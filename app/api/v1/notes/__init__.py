from fastapi import APIRouter
from .notes import router

notes_router = APIRouter()

notes_router.include_router(router,tags=["notes模块"])
