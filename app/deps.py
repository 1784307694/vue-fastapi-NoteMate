"""
依赖注入管理
用于管理FastAPI的依赖注入，如数据库会话、认证等
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 在这里添加你的依赖函数 