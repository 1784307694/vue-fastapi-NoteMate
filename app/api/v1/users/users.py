"""
用户管理模块路由

提供用户管理相关的API接口, 包括:
- 用户列表查询(支持分页和过滤)
- 用户详情查看
- 用户创建(包含角色分配)
- 用户更新
- 用户删除
- 密码重置
"""

import logging
from fastapi import APIRouter, Body, Query
from tortoise.expressions import Q
from typing import Optional, List
from datetime import datetime

from app.controllers.user import user_controller
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.users import *

# 创建日志记录器
logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter()


@router.get("/list", summary="查看用户列表")
async def list_user(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    username: str = Query(None, description="用户名称"),
    email: str = Query(None, description="邮箱地址"),
    phone: str = Query(None, description="手机号码"),
    is_active: bool = Query(None, description="状态"),
    start_time: str = Query("", description="开始时间"),
    end_time: str = Query("", description="结束时间"),
):
    """获取用户列表
    
    支持分页查询和条件过滤
    
    Args:
        page: 当前页码, 默认1
        page_size: 每页数量, 默认10
        username: 用户名称, 支持模糊匹配
        email: 邮箱地址, 支持模糊匹配
        phone: 手机号码, 支持模糊匹配
        is_active: 用户状态(True-启用 False-禁用)
        created_at: 创建时间范围[开始时间, 结束时间]
        
    Returns:
        SuccessExtra: 包含分页数据的响应对象
            - data: 用户列表数据(不包含密码字段)
            - total: 总记录数
            - page: 当前页码
            - page_size: 每页数量
    """
    # 构建查询条件
    q = Q()
    if username:
        q &= Q(username__icontains=username)  # 使用icontains实现不区分大小写的模糊查询
    if email:
        q &= Q(email__icontains=email)
    if phone:
        q &= Q(phone__icontains=phone)
    if is_active is not None:  # 显式检查是否为None，因为False也是有效值
        q &= Q(is_active=is_active)
    # 处理时间范围查询
    if start_time and end_time:
        q &= Q(created_at__range=[start_time, end_time])
    elif start_time:
        q &= Q(created_at__gte=start_time)
    elif end_time:
        q &= Q(created_at__lte=end_time)
        
    # 执行分页查询
    total, user_objs = await user_controller.list(
        page=page, 
        page_size=page_size, 
        search=q,
        order=["-created_at"]  # 按创建时间倒序排序
    )
    
    # 转换数据格式, 排除密码字段
    data = [
        await obj.to_dict(
            m2m=True,  # 包含多对多关系(角色信息)
            exclude_fields=["password"]  # 排除密码字段
        ) 
        for obj in user_objs
    ]
    
    return SuccessExtra(
        data=data,
        total=total,
        page=page,
        page_size=page_size
    )



@router.post("/create", summary="创建用户")
async def create_user(
    user_in: UserCreate,
):
    """创建新用户
    
    创建用户并分配角色
    
    Args:
        user_in: 用户创建模型, 包含:
            - 基本信息(用户名、邮箱等)
            - 角色ID列表
            
    Returns:
        Success/Fail: 创建成功或失败的响应对象
            - 如果邮箱已存在, 返回400错误
            - 创建成功返回成功消息
            
    Note:
        创建用户后会自动更新用户的角色关系
    """
    # 检查手机号是否已存在
    if user_in.phone:
        user = await user_controller.get_by_phone(user_in.phone)
    # 检查用户名是否已存在
    if user_in.username:
        user = await user_controller.get_by_username(user_in.username)
    # 检查邮箱是否已存在
    if user_in.email:
        user = await user_controller.get_by_email(user_in.email)
    if user:
        return Fail(code=400, msg="The user already exists in the system.")
    # 创建用户
    new_user = await user_controller.create_user(obj_in=user_in)
    # 更新用户角色
    await user_controller.update_roles(new_user, user_in.role_ids)
    return Success(msg="Created Successfully")

@router.get("/get", summary="查看用户")
async def get_user(
    user_id: int = Query(..., description="用户ID"),
):
    """获取单个用户详情
    
    Args:
        user_id: 用户ID
        
    Returns:
        Success: 包含用户详情的响应对象
            - data: 用户详细信息(不包含密码字段)
    """
    user_obj = await user_controller.get(id=user_id)
    user_dict = await user_obj.to_dict(exclude_fields=["password"])
    return Success(data=user_dict)




@router.post("/update", summary="更新用户")
async def update_user(
    user_in: UserUpdate,
):
    """更新用户信息
    
    更新用户基本信息和角色关系
    
    Args:
        user_in: 用户更新模型, 包含:
            - 用户ID
            - 要更新的字段
            - 角色ID列表
            
    Returns:
        Success: 更新成功的响应对象
        
    Note:
        会同时更新用户的角色关系
    """
    # 更新用户基本信息
    user = await user_controller.update(id=user_in.id, obj_in=user_in)
    # 更新用户角色
    await user_controller.update_roles(user, user_in.role_ids)
    return Success(msg="Updated Successfully")


@router.delete("/delete", summary="删除用户")
async def delete_user(
    user_id: int = Query(..., description="用户ID"),
):
    """删除指定用户
    
    Args:
        user_id: 要删除的用户ID
        
    Returns:
        Success: 删除成功的响应对象
        
    Note:
        会同时删除用户的角色关系
    """
    await user_controller.remove(id=user_id)
    return Success(msg="Deleted Successfully")


@router.post("/reset_password", summary="重置密码")
async def reset_password(user_id: int = Body(..., description="用户ID", embed=True)):
    """重置用户密码
    
    将用户密码重置为默认密码(123456)
    
    Args:
        user_id: 要重置密码的用户ID
        
    Returns:
        Success: 重置成功的响应对象
    """
    await user_controller.reset_password(user_id)
    return Success(msg="密码已重置为123456")

