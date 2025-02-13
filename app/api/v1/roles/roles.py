import logging

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from tortoise.expressions import Q
from typing import Optional, List

from app.controllers.role import role_controller
from app.schemas.base import Success, SuccessExtra
from app.schemas.roles import *

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/list", summary="查看角色列表")
async def list_role(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    role_name: str = Query("", description="角色名称，用于查询"),
    start_time: str = Query("", description="开始时间"),
    end_time: str = Query("", description="结束时间"),
):
    """获取角色列表
    
    支持按角色名称搜索和时间范围过滤
    
    Args:
        page: 当前页码
        page_size: 每页数量
        role_name: 角色名称(模糊匹配)
        start_time: 开始时间
        end_time: 结束时间
    """
    # 构建查询条件
    q = Q()
    if role_name:
        q &= Q(name__icontains=role_name)  # 使用icontains实现不区分大小写的模糊查询
        
    # 处理时间范围查询
    if start_time and end_time:
        q &= Q(created_at__range=[start_time, end_time])
    elif start_time:
        q &= Q(created_at__gte=start_time)
    elif end_time:
        q &= Q(created_at__lte=end_time)
        
    # 执行查询
    total, role_objs = await role_controller.list(
        page=page, 
        page_size=page_size, 
        search=q,
        order=["-created_at"]  # 按创建时间倒序排序
    )
    
    # 转换数据
    data = [await obj.to_dict() for obj in role_objs]
    
    return SuccessExtra(
        data=data, 
        total=total, 
        page=page, 
        page_size=page_size
    )


@router.get("/get", summary="查看角色")
async def get_role(
    role_id: int = Query(..., description="角色ID"),
):
    role_obj = await role_controller.get(id=role_id)
    return Success(data=await role_obj.to_dict())


@router.post("/create", summary="创建角色")
async def create_role(role_in: RoleCreate):
    if await role_controller.is_exist(name=role_in.name):
        raise HTTPException(
            status_code=400,
            detail="The role with this rolename already exists in the system.",
        )
    await role_controller.create(obj_in=role_in)
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新角色")
async def update_role(role_in: RoleUpdate):
    await role_controller.update(id=role_in.id, obj_in=role_in)
    return Success(msg="Updated Successfully")


@router.delete("/delete", summary="删除角色")
async def delete_role(
    role_id: int = Query(..., description="角色ID"),
):
    await role_controller.remove(id=role_id)
    return Success(msg="Deleted Success")


@router.get("/authorized", summary="查看角色权限")
async def get_role_authorized(id: int = Query(..., description="角色ID")):
    role_obj = await role_controller.get(id=id)
    data = await role_obj.to_dict(m2m=True)
    return Success(data=data)


@router.post("/authorized", summary="更新角色权限")
async def update_role_authorized(role_in: RoleUpdateMenusApis):
    role_obj = await role_controller.get(id=role_in.id)
    await role_controller.update_roles(role=role_obj, menu_ids=role_in.menu_ids, api_infos=role_in.api_infos)
    return Success(msg="Updated Successfully")
