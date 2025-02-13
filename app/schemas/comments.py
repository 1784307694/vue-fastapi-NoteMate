"""
评论相关的数据模型定义

包含以下模型:
- BaseComment: 评论基础模型, 用于评论信息的展示
- CommentCreate: 评论创建模型, 用于创建新评论
- CommentUpdate: 评论更新模型, 用于更新已有评论
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class BaseComment(BaseModel):
    """评论基础模型
    
    用于评论信息的展示, 包含评论的所有基础字段
    
    Attributes:
        id: 评论ID
        note_id: 笔记ID
        user_id: 评论用户ID
        content: 评论内容
        parent_id: 父评论ID, 用于回复功能
        root_id: 根评论ID, 用于快速获取评论树
        like_count: 点赞数
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    note_id: int
    user_id: int
    content: str
    parent_id: Optional[int]
    root_id: Optional[int]
    like_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    """评论创建模型
    
    用于创建新评论时的数据验证
    
    Attributes:
        note_id: 笔记ID
        content: 评论内容
        parent_id: 父评论ID(可选), 用于回复功能
    """
    note_id: int
    content: str = Field(example="这是一条评论")
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    """评论更新模型
    
    用于更新已有评论时的数据验证
    
    Attributes:
        id: 评论ID
        content: 评论内容
    """
    id: int
    content: str 