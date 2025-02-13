from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CredentialsSchema(BaseModel):
    loginType: str = Field(..., description="登录方式", example="username")
    username: str = Field(None, description="用户名称", example="admin")
    password: str = Field(None, description="密码", example="123456")
    email: str = Field(None, description="邮箱", example="admin@example.com")
    phone: str = Field(None, description="手机号", example="13800138000")
    code: str = Field(None, description="验证码", example="123456")


class JWTOut(BaseModel):
    access_token: str
    username: str


class JWTPayload(BaseModel):
    user_id: int
    username: str
    is_superuser: bool
    exp: datetime
