"""
笔记相关的数据模型定义

包含以下模型:
- BaseNote: 笔记基础模型, 用于笔记信息的展示
- NoteCreate: 笔记创建模型, 用于创建新笔记
- NoteUpdate: 笔记更新模型, 用于更新已有笔记
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class BaseNote(BaseModel):
    """笔记基础模型
    
    用于笔记信息的展示, 包含笔记的所有基础字段
    
    Attributes:
        id: 笔记ID
        user_id: 作者ID
        title: 笔记标题
        content: 笔记内容
        type: 笔记类型(0-免费 1-付费)
        price: 笔记价格
        status: 笔记状态(0-私有 1-公开 2-审核中)
        view_count: 浏览次数
        like_count: 点赞次数
        buy_count: 购买次数
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    user_id: int
    title: str
    content: str
    type: int = Field(description="类型: 0-免费 1-付费")
    price: Decimal = Field(default=0, description="价格")
    status: int = Field(description="状态: 0-私有 1-公开 2-审核中")
    view_count: int = Field(default=0)
    like_count: int = Field(default=0)
    buy_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime


class KnowledgeBasesCreate(BaseModel):
    """创建知识库请求模型"""
    name: str = Field(..., description="知识库名称")
    type: int = Field(0, description="类型: 0-私有 1-公开")


class KnowledgeBasesUpdate(BaseModel):
    """更新知识库请求模型"""
    id: int = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    type: int = Field(0, description="类型: 0-私有 1-公开")


class NoteCreate(BaseModel):
    """创建笔记请求模型"""
    knowledge_bases_id: int = Field(..., description="知识库ID")
    title: str = Field(..., description="标题")
    cover: Optional[str] = Field(None, description="封面")
    introduction: Optional[str] = Field(None, description="简介")
    content: str = Field('', description="笔记内容")
    type: int = Field(0, description="类型: 0-免费 1-付费")
    price: Decimal = Field(0, description="价格")
    status: int = Field(1, description="状态: 0-私有 1-公开 2-审核中")


class NoteUpdate(BaseModel):
    """更新笔记请求模型"""
    id: int = Field(..., description="笔记ID")
    title: str = Field(..., description="标题")
    cover: Optional[str] = Field(None, description="封面")
    introduction: Optional[str] = Field(None, description="简介")
    type: int = Field(0, description="类型: 0-免费 1-付费")
    price: Decimal = Field(0, description="价格")
    status: int = Field(1, description="状态: 0-私有 1-公开 2-审核中")
    
    
    

