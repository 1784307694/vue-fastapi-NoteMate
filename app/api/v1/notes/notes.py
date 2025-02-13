import logging
import uuid
from datetime import datetime
import json

from fastapi import APIRouter, Query, Depends
from fastapi.exceptions import HTTPException
from tortoise.expressions import Q
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis import Redis

from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth, DependMongoDB, RedisControl
from app.schemas.base import Success, SuccessExtra, Fail
from app.schemas.notes import *
from app.models.admin import KnowledgeBases, Note, User
from app.utils.redis_cache import RedisCache
from app.utils.redis import RedisUtils

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/knowledge_bases_list", summary="获取用户全部知识库")
async def get_all_knowledge_bases(
    user_id: int = Query(..., description="用户ID"),
    redis: Redis = Depends(RedisControl.get_redis)
):
    """获取用户全部知识库"""
    # 先尝试从缓存获取
    cached_knowledge_bases = await RedisCache.get_knowledge_bases(redis, user_id)
    if cached_knowledge_bases:
        return Success(data=cached_knowledge_bases)
    
    # 缓存未命中，从数据库查询
    knowledge_bases = await KnowledgeBases.filter(user_id=user_id).all()
    data = [await kb.to_dict() for kb in knowledge_bases]
    
    # 写入缓存
    await RedisCache.set_knowledge_bases(redis, user_id, data)
    return Success(data=data)


@router.post("/create_knowledge_bases", summary="创建知识库", dependencies=[DependAuth])
async def create_knowledge_bases(
    knowledge_bases: KnowledgeBasesCreate,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """创建知识库"""
    user_id = CTX_USER_ID.get()
    knowledge_bases_obj = await KnowledgeBases.create(
        user_id=user_id,
        name=knowledge_bases.name,
        type=knowledge_bases.type
    )
    
    # 清除知识库列表缓存
    await RedisCache.delete_knowledge_bases(redis, user_id)
    return Success(msg="知识库创建成功")


@router.post("/update_knowledge_bases", summary="更新知识库", dependencies=[DependAuth])
async def update_knowledge_bases(
    knowledge_bases: KnowledgeBasesUpdate,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """更新知识库"""
    knowledge_bases_obj = await KnowledgeBases.filter(id=knowledge_bases.id).first()
    if not knowledge_bases_obj:
        raise HTTPException(status_code=400, detail="知识库不存在")
    
    # 更新知识库
    knowledge_bases_obj.name = knowledge_bases.name
    knowledge_bases_obj.type = knowledge_bases.type
    await knowledge_bases_obj.save()
    
    # 清除相关缓存
    await RedisCache.clear_knowledge_base_cache(redis, knowledge_bases_obj.user_id, knowledge_bases_obj.id)
    return Success(msg="知识库更新成功")


@router.delete("/delete_knowledge_bases", summary="删除知识库", dependencies=[DependAuth])
async def delete_knowledge_bases(
    id: int,
    mongodb: AsyncIOMotorDatabase = DependMongoDB,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """删除知识库及其所有笔记"""
    # 检查知识库是否存在
    knowledge_bases = await KnowledgeBases.filter(id=id).first()
    if not knowledge_bases:
        raise HTTPException(status_code=400, detail="知识库不存在")
    
    # 检查是否是笔记作者
    user_id = CTX_USER_ID.get()
    if knowledge_bases.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限删除此知识库")
    
    # 获取该知识库下的所有笔记
    notes = await Note.filter(knowledge_bases_id=id).all()
    
    # 删除MongoDB中的笔记内容
    if notes:
        content_keys = [note.content for note in notes]
        await mongodb.note_contents.delete_many({"key": {"$in": content_keys}})
    
    # 删除所有笔记
    await Note.filter(knowledge_bases_id=id).delete()
    
    # 删除知识库
    await knowledge_bases.delete()
    
    # 清除相关缓存
    await RedisCache.clear_knowledge_base_cache(redis, knowledge_bases.user_id, id)
    return Success(msg="知识库及其笔记删除成功")


@router.get("/knowledge_bases_notes_list", summary="获取知识库笔记列表")
async def get_notes_list(
    knowledge_bases_id: int = Query(..., description="知识库ID"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    status: Optional[int] = Query(None, description="状态: 0-私有 1-公开 2-审核中"),
    type: Optional[int] = Query(None, description="类型: 0-免费 1-付费"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    redis: Redis = Depends(RedisControl.get_redis)
):
    """获取笔记列表，支持分页、状态筛选和关键词搜索"""
    # 如果没有筛选条件，尝试从缓存获取
    if status is None and type is None and not keyword:
        cached_notes = await RedisCache.get_knowledge_base_notes(redis, knowledge_bases_id, page)
        if cached_notes:
            return SuccessExtra(**cached_notes)
    
    # 构建查询条件
    query = Q(knowledge_bases_id=knowledge_bases_id)
    if status is not None:
        query &= Q(status=status)
    if type is not None:
        query &= Q(type=type)
    if keyword:
        query &= (Q(title__icontains=keyword) | Q(introduction__icontains=keyword))
    
    # 计算总数
    total = await Note.filter(query).count()
    
    # 获取分页数据
    notes = await Note.filter(query).offset((page - 1) * page_size).limit(page_size).all()
    
    # 处理数据
    data = []
    for note in notes:
        note_dict = await note.to_dict()
        if 'price' in note_dict:
            note_dict['price'] = float(note_dict['price'])
        data.append(note_dict)
    
    result = {
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    
    # 如果没有筛选条件，写入缓存
    if status is None and type is None and not keyword:
        await RedisCache.set_knowledge_base_notes(redis, knowledge_bases_id, page, result)
    
    return SuccessExtra(**result)


@router.get("/note_detail", summary="获取笔记详情")
async def get_note_detail(
    note_id: int = Query(..., description="笔记ID"),
    mongodb: AsyncIOMotorDatabase = DependMongoDB,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """获取笔记详情"""
    # 先尝试从缓存获取
    cached_note = await RedisCache.get_note_content(redis, note_id)
    if cached_note:
        return Success(data=cached_note)
    
    # 缓存未命中，从数据库查询
    note = await Note.filter(id=note_id).first()
    if not note:
        raise HTTPException(status_code=400, detail="笔记不存在")
    
    # 增加浏览次数
    note.view_count += 1
    await note.save()
    
    # 获取笔记基本信息
    data = await note.to_dict()
    
    # 处理 Decimal 类型
    if 'price' in data:
        data['price'] = str(data['price'])
        
    # 获取作者信息
    user = await User.get_or_none(id=note.user_id)
    data["author_name"] = user.username if user else ""
    data["author_avatar"] = user.avatar if user else ""
    
    # 从MongoDB获取笔记内容
    content_doc = await mongodb.note_contents.find_one({"key": note.content})
    if content_doc:
        data["content"] = content_doc["content"]
    else:
        data["content"] = ""
    
    # 写入缓存
    await RedisCache.set_note_content(redis, note_id, data)
    
    return Success(data=data)


@router.post("/create_note", summary="创建笔记", dependencies=[DependAuth])
async def create_note(
    note: NoteCreate,
    mongodb: AsyncIOMotorDatabase = DependMongoDB,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """创建笔记"""
    user_id = CTX_USER_ID.get()
    
    # 检查知识库是否存在
    knowledge_base = await KnowledgeBases.filter(id=note.knowledge_bases_id).first()
    if not knowledge_base:
        raise HTTPException(status_code=400, detail="知识库不存在")
    
    # 生成MongoDB中存储内容的key
    content_key = str(uuid.uuid4())
    
    # 将内容存储到MongoDB
    await mongodb.note_contents.insert_one({
        "key": content_key,
        "content": note.content,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    
    # 创建笔记
    note_obj = await Note.create(
        user_id=user_id,
        knowledge_bases_id=note.knowledge_bases_id,
        title=note.title,
        cover=note.cover,
        introduction=note.introduction,
        content=content_key,
        type=note.type,
        price=note.price,
        status=note.status
    )
    
    # 处理返回数据
    data = await note_obj.to_dict(exclude_fields=["content"])
    if 'price' in data:
        data['price'] = str(data['price'])
    
    # 清除用户笔记列表缓存
    await RedisCache.delete_user_notes(redis, user_id)
    # 清除知识库笔记列表缓存
    await RedisCache.delete_knowledge_base_notes(redis, note.knowledge_bases_id)
    
    # 设置新笔记的缓存
    await RedisCache.set_note_content(redis, note_obj.id, data)
    
    return Success(data=data, msg="笔记创建成功")


@router.post("/update_note", summary="更新笔记", dependencies=[DependAuth])
async def update_note(
    note: NoteUpdate,
    mongodb: AsyncIOMotorDatabase = DependMongoDB,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """更新笔记基本信息"""
    note_obj = await Note.filter(id=note.id).first()
    if not note_obj:
        raise HTTPException(status_code=400, detail="笔记不存在")
    
    # 检查是否是笔记作者
    user_id = CTX_USER_ID.get()
    if note_obj.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限修改此笔记")
    
    # 只更新前端传递的字段
    update_data = {}
    for field, value in note.model_dump(exclude_unset=True).items():
        if value is not None and field != "id" and field != "content":
            update_data[field] = value
    
    if update_data:
        await note_obj.update_from_dict(update_data)
        await note_obj.save()
    
    # 清除相关缓存
    await RedisCache.delete_note_content(redis, note.id)
    await RedisCache.delete_user_notes(redis, user_id)
    # 清除知识库笔记列表缓存
    await RedisCache.delete_knowledge_base_notes(redis, note_obj.knowledge_bases_id)
    
    # 更新笔记基本信息缓存
    note_dict = await note_obj.to_dict()
    if 'price' in note_dict:
        note_dict['price'] = float(note_dict['price'])
    
    # 从 MongoDB 获取笔记内容
    content_doc = await mongodb.note_contents.find_one({"key": note_obj.content})
    if content_doc:
        note_dict["content"] = content_doc["content"]
    else:
        note_dict["content"] = ""
        
    await RedisCache.set_note_content(redis, note.id, note_dict)
    
    return Success(msg="笔记更新成功")


@router.delete("/delete_note", summary="删除笔记", dependencies=[DependAuth])
async def delete_note(
    note_id: int = Query(..., description="笔记ID"),
    mongodb: AsyncIOMotorDatabase = DependMongoDB,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """
    删除笔记
    """
    note = await Note.filter(id=note_id).first()
    if not note:
        raise HTTPException(status_code=400, detail="笔记不存在")
    
    # 检查是否是笔记作者
    user_id = CTX_USER_ID.get()
    if note.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限删除此笔记")
    
    # 删除MongoDB中的内容
    await mongodb.note_contents.delete_one({"key": note.content})
    
    # 删除笔记
    await note.delete()
    
    # 清除相关缓存
    await RedisCache.delete_note_content(redis, note_id)
    await RedisCache.delete_user_notes(redis, user_id)
    await RedisCache.delete_knowledge_base_notes(redis, note.knowledge_bases_id)

    return Success(msg="笔记删除成功")


@router.post("/update_note_content", summary="更新笔记正文", dependencies=[DependAuth])
async def update_note_content(
    note_id: int = Query(..., description="笔记ID"),
    content: str = Query(..., description="笔记内容"),
    mongodb: AsyncIOMotorDatabase = DependMongoDB,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """
    更新笔记正文
    内容存储在 MongoDB 中
    """
    # 检查笔记是否存在
    note = await Note.filter(id=note_id).first()
    if not note:
        raise HTTPException(status_code=400, detail="笔记不存在")
    
    # 检查是否是笔记作者
    user_id = CTX_USER_ID.get()
    if note.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限修改此笔记")
    
    # 更新MongoDB中的内容
    result = await mongodb.note_contents.update_one(
        {"key": note.content},
        {
            "$set": {
                "content": content,
                "updated_at": datetime.now()
            }
        }
    )
    
    if result.modified_count == 0:
        # 如果没有更新成功，可能是内容不存在，需要重新创建
        await mongodb.note_contents.insert_one({
            "key": note.content,
            "content": content,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
    
    # 更新笔记内容缓存
    note_dict = await note.to_dict()
    # 处理 Decimal 类型
    if 'price' in note_dict:
        note_dict['price'] = str(note_dict['price'])
    note_dict["content"] = content
    await RedisCache.set_note_content(redis, note_id, note_dict)
    
    return Success(msg="笔记内容更新成功")


@router.get("/list", summary="获取笔记列表")
async def get_notes(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    type: Optional[int] = Query(None, description="类型: 0-免费 1-付费"),
    status: Optional[int] = Query(1, description="状态: 0-私有 1-公开 2-审核中"),
    min_price: Optional[float] = Query(None, description="最小价格"),
    max_price: Optional[float] = Query(None, description="最大价格"),
    redis: Redis = Depends(RedisControl.get_redis)
):
    """获取所有笔记列表
    
    支持按类型、状态、价格范围筛选
    返回数据包含作者名称和知识库名称
    使用Redis缓存查询结果
    """
    # 构建缓存键
    cache_key = f"notes_list_{page}_{page_size}_{type}_{status}_{min_price}_{max_price}"
    
    # 尝试从缓存获取
    cached_data = await RedisUtils.cache_get(redis, cache_key)
    if cached_data:
        return SuccessExtra(**json.loads(cached_data))
    
    # 构建查询条件
    query = Q()
    if type is not None:
        query &= Q(type=type)
    if status is not None:
        query &= Q(status=status)
    if min_price is not None:
        query &= Q(price__gte=min_price)
    if max_price is not None:
        query &= Q(price__lte=max_price)
    
    total = await Note.filter(query).count()
    
    notes = await Note.filter(query).offset((page - 1) * page_size).limit(page_size).all()
    
    data = []
    for note in notes:
        # 获取笔记基本信息，排除content字段
        note_dict = await note.to_dict(exclude_fields=["content"])
        
        # 获取作者信息
        user = await User.get_or_none(id=note.user_id)
        note_dict["author_name"] = user.username if user else ""
        note_dict["author_avatar"] = user.avatar if user else ""
        
        # 获取知识库信息
        kb = await KnowledgeBases.get_or_none(id=note.knowledge_bases_id)
        note_dict["knowledge_base_name"] = kb.name if kb else ""
        
        # 处理价格字段
        if 'price' in note_dict:
            note_dict['price'] = float(note_dict['price'])
            
        data.append(note_dict)
    
    result = {
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    
    # 写入缓存，设置5分钟过期
    await RedisUtils.cache_set(redis, cache_key, json.dumps(result), expire=300)
    
    return SuccessExtra(**result)







