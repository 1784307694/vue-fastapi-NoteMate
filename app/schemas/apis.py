"""
API相关的数据模型定义

包含以下模型:
- BaseApi: API基础模型, 用于API信息的展示
- ApiCreate: API创建模型, 用于创建新API
- ApiUpdate: API更新模型, 用于更新已有API
"""

from pydantic import BaseModel, Field

from app.models.enums import MethodType


class BaseApi(BaseModel):
    """API基础模型
    
    用于API信息的展示, 包含API的所有基础字段
    
    Attributes:
        path: API路径, 例如: /api/v1/user/list
        summary: API简介, 用于描述API的功能
        method: API请求方法(GET, POST, PUT, DELETE等)
        tags: API标签, 用于API分组
    """
    path: str = Field(..., description="API路径", example="/api/v1/user/list")
    summary: str = Field("", description="API简介", example="查看用户列表")
    method: MethodType = Field(..., description="API方法", example="GET")
    tags: str = Field(..., description="API标签", example="User")


class ApiCreate(BaseApi):
    """API创建模型
    
    用于创建新API时的数据验证, 继承自BaseApi
    包含API的基本信息字段
    """
    pass


class ApiUpdate(BaseApi):
    """API更新模型
    
    用于更新已有API时的数据验证, 继承自BaseApi
    
    Attributes:
        id: API ID, 用于标识要更新的API
    """
    id: int
