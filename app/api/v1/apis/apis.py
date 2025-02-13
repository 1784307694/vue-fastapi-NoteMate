"""
API路由模块

提供API管理相关的路由处理, 包括:
- API列表的查询和过滤
- API的创建、更新、删除
- API列表的自动刷新
"""

from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.controllers.api import api_controller
from app.schemas import Success, SuccessExtra
from app.schemas.apis import *

# 创建路由实例
router = APIRouter()


@router.get("/list", summary="查看API列表")
async def list_api(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    path: str = Query(None, description="API路径"),
    summary: str = Query(None, description="API简介"),
    method: str = Query(None, description="请求方法"),
    tags: str = Query(None, description="API模块"),
):
    """获取API列表
    
    支持分页查询和多条件过滤
    
    Args:
        page: 当前页码, 默认1
        page_size: 每页数量, 默认10
        path: API路径, 支持模糊匹配
        summary: API简介, 支持模糊匹配
        tags: API模块标签, 支持模糊匹配
        
    Returns:
        SuccessExtra: 包含分页数据的响应对象
            - data: API列表数据
            - total: 总记录数
            - page: 当前页码
            - page_size: 每页数量
    """
    # 构建查询条件
    q = Q()
    if path:
        # __contains模糊匹配
        q &= Q(path__contains=path)
    if summary:
        q &= Q(summary__contains=summary)
    if tags:
        q &= Q(tags__contains=tags)
    if method:
        q &= Q(method=method)
        


    # 执行分页查询
    total, api_objs = await api_controller.list(
        page=page,
        page_size=page_size,
        search=q,
        order=["tags", "id"]
    )
    
    # 转换数据格式
    data = [await obj.to_dict() for obj in api_objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看Api")
async def get_api(
    id: int = Query(..., description="Api"),
):
    """获取单个API详情
    
    Args:
        id: API ID
        
    Returns:
        Success: 包含API详情的响应对象
            - data: API详细信息
    """
    api_obj = await api_controller.get(id=id)
    data = await api_obj.to_dict()
    return Success(data=data)


@router.post("/create", summary="创建Api")
async def create_api(
    api_in: ApiCreate,
):
    """创建新的API
    
    Args:
        api_in: API创建模型, 包含API的基本信息
        
    Returns:
        Success: 创建成功的响应对象
    """
    await api_controller.create(obj_in=api_in)
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新Api")
async def update_api(
    api_in: ApiUpdate,
):
    """更新已有的API
    
    Args:
        api_in: API更新模型, 包含要更新的API信息
        
    Returns:
        Success: 更新成功的响应对象
    """
    await api_controller.update(id=api_in.id, obj_in=api_in)
    return Success(msg="Update Successfully")


@router.delete("/delete", summary="删除Api")
async def delete_api(
    api_id: int = Query(..., description="ApiID"),
):
    """删除指定的API
    
    Args:
        api_id: 要删除的API ID
        
    Returns:
        Success: 删除成功的响应对象
    """
    await api_controller.remove(id=api_id)
    return Success(msg="Deleted Success")


@router.post("/refresh", summary="刷新API列表")
async def refresh_api():
    """刷新API列表
    
    自动扫描所有路由并更新API数据库记录
    
    Returns:
        Success: 刷新成功的响应对象
    """
    await api_controller.refresh_api()
    return Success(msg="OK")
