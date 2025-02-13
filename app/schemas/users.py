from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

class BaseUser(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    roles: Optional[list] = []
    
    
class UserCreate(BaseModel):
    phone: Optional[str] = Field(default=None, example="13800138000")
    email: Optional[EmailStr] = Field(default=None, example="admin@example.com") 
    username: str = Field(example="admin")
    password: Optional[str] = Field(default=None, example="123456")
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role_ids: Optional[List[int]] = []

    def create_dict(self):
        return self.model_dump(exclude_unset=True, exclude={"role_ids"})


class BaseUserCreate(BaseModel):
    phone: Optional[str] = Field(default=None, example="13800138000")
    email: Optional[EmailStr] = Field(default=None, example="admin@example.com") 
    username: str = Field(default=None, example="admin")
    password: Optional[str] = Field(default=None, example="123456")
    code: Optional[str] = Field(default=None, example="123456")
    
    


class UserUpdate(BaseModel):
    id: int
    email: EmailStr
    phone: str
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role_ids: Optional[List[int]] = []

class UpdateBaseUserInfo(BaseModel):
    email: EmailStr
    phone: str
    username: str


class UpdatePassword(BaseModel):
    email: EmailStr
    code: str
    password: str = Field(description="新密码")
