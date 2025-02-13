from typing import Any, List, Optional, Union
import json
from redis import Redis
from app.utils.redis import RedisUtils

class RedisCacheKey:
    """Redis缓存键定义"""
    # 验证码
    EMAIL_CODE = "email_{}"  # email
    
    # 用户相关
    USER_PERMISSIONS = "permissions_{}"  # user_id
    USER_MENUS = "menus_{}"  # user_id
    
    # 接口限流
    RATE_LIMIT = "rate_limit_{}_{}"  # ip, api_path
    USER_LIMIT = "user_limit_{}_{}"  # user_id, operation
    
    # 笔记相关
    HOT_NOTES = "hot_notes"
    NOTE_CONTENT = "note_{}"  # note_id
    USER_NOTES = "user_notes_{}"  # user_id
    KNOWLEDGE_BASES = "knowledge_bases_{}"  # user_id
    KNOWLEDGE_BASE_NOTES = "knowledge_base_notes_{}_{}"  # knowledge_base_id, page
    
    # 系统配置
    SYSTEM_CONFIG = "system_config"
    ROLE_PERMISSIONS = "role_permissions_{}"  # role_id

class RedisCache:
    """Redis缓存工具类"""
    
    @staticmethod
    async def set_user_permissions(redis: Redis, user_id: int, permissions: List[str], expire: int = 1800) -> bool:
        """设置用户权限缓存
        
        Args:
            redis: Redis连接
            user_id: 用户ID
            permissions: 权限列表
            expire: 过期时间(秒)，默认30分钟
        """
        key = RedisCacheKey.USER_PERMISSIONS.format(user_id)
        return await RedisUtils.cache_set(redis, key, json.dumps(permissions), expire=expire)
    
    @staticmethod
    async def get_user_permissions(redis: Redis, user_id: int) -> Optional[List[str]]:
        """获取用户权限缓存"""
        key = RedisCacheKey.USER_PERMISSIONS.format(user_id)
        data = await RedisUtils.cache_get(redis, key)
        return json.loads(data) if data else None
    
    @staticmethod
    async def set_user_menus(redis: Redis, user_id: int, menus: List[dict], expire: int = 1800) -> bool:
        """设置用户菜单缓存"""
        key = RedisCacheKey.USER_MENUS.format(user_id)
        return await RedisUtils.cache_set(redis, key, json.dumps(menus), expire=expire)
    
    @staticmethod
    async def get_user_menus(redis: Redis, user_id: int) -> Optional[List[dict]]:
        """获取用户菜单缓存"""
        key = RedisCacheKey.USER_MENUS.format(user_id)
        data = await RedisUtils.cache_get(redis, key)
        return json.loads(data) if data else None
    
    @staticmethod
    async def set_note_content(redis: Redis, note_id: int, content: dict, expire: int = 600) -> bool:
        """设置笔记内容缓存"""
        key = RedisCacheKey.NOTE_CONTENT.format(note_id)
        return await RedisUtils.cache_set(redis, key, json.dumps(content), expire=expire)
    
    @staticmethod
    async def get_note_content(redis: Redis, note_id: int) -> Optional[dict]:
        """获取笔记内容缓存"""
        key = RedisCacheKey.NOTE_CONTENT.format(note_id)
        data = await RedisUtils.cache_get(redis, key)
        return json.loads(data) if data else None
    
    @staticmethod
    async def set_user_notes(redis: Redis, user_id: int, notes: List[dict], expire: int = 300) -> bool:
        """设置用户笔记列表缓存"""
        key = RedisCacheKey.USER_NOTES.format(user_id)
        return await RedisUtils.cache_set(redis, key, json.dumps(notes), expire=expire)
    
    @staticmethod
    async def get_user_notes(redis: Redis, user_id: int) -> Optional[List[dict]]:
        """获取用户笔记列表缓存"""
        key = RedisCacheKey.USER_NOTES.format(user_id)
        data = await RedisUtils.cache_get(redis, key)
        return json.loads(data) if data else None
    
    @staticmethod
    async def increment_rate_limit(redis: Redis, ip: str, api_path: str, expire: int = 60) -> int:
        """增加接口访问计数"""
        key = RedisCacheKey.RATE_LIMIT.format(ip, api_path)
        count = await RedisUtils.cache_incr(redis, key)
        if count == 1:
            await RedisUtils.cache_expire(redis, key, expire)
        return count
    
    @staticmethod
    async def check_rate_limit(redis: Redis, ip: str, api_path: str, limit: int = 60) -> bool:
        """检查接口访问是否超限"""
        key = RedisCacheKey.RATE_LIMIT.format(ip, api_path)
        count = await RedisUtils.cache_get(redis, key)
        return int(count or 0) < limit
        
    @staticmethod
    async def delete_user_permissions(redis: Redis, user_id: int) -> bool:
        """删除用户权限缓存"""
        key = RedisCacheKey.USER_PERMISSIONS.format(user_id)
        return await RedisUtils.cache_delete(redis, key)
        
    @staticmethod
    async def delete_user_menus(redis: Redis, user_id: int) -> bool:
        """删除用户菜单缓存"""
        key = RedisCacheKey.USER_MENUS.format(user_id)
        return await RedisUtils.cache_delete(redis, key)
        
    @staticmethod
    async def delete_note_content(redis: Redis, note_id: int) -> bool:
        """删除笔记内容缓存"""
        key = RedisCacheKey.NOTE_CONTENT.format(note_id)
        return await RedisUtils.cache_delete(redis, key)
        
    @staticmethod
    async def delete_user_notes(redis: Redis, user_id: int) -> bool:
        """删除用户笔记列表缓存"""
        key = RedisCacheKey.USER_NOTES.format(user_id)
        return await RedisUtils.cache_delete(redis, key)
        
    @staticmethod
    async def clear_user_cache(redis: Redis, user_id: int) -> None:
        """清除用户所有相关缓存"""
        await RedisCache.delete_user_permissions(redis, user_id)
        await RedisCache.delete_user_menus(redis, user_id)
        await RedisCache.delete_user_notes(redis, user_id)
    
    @staticmethod
    async def set_knowledge_bases(redis: Redis, user_id: int, knowledge_bases: List[dict], expire: int = 300) -> bool:
        """设置用户知识库列表缓存"""
        key = RedisCacheKey.KNOWLEDGE_BASES.format(user_id)
        return await RedisUtils.cache_set(redis, key, json.dumps(knowledge_bases), expire=expire)
    
    @staticmethod
    async def get_knowledge_bases(redis: Redis, user_id: int) -> Optional[List[dict]]:
        """获取用户知识库列表缓存"""
        key = RedisCacheKey.KNOWLEDGE_BASES.format(user_id)
        data = await RedisUtils.cache_get(redis, key)
        return json.loads(data) if data else None
    
    @staticmethod
    async def delete_knowledge_bases(redis: Redis, user_id: int) -> bool:
        """删除用户知识库列表缓存"""
        key = RedisCacheKey.KNOWLEDGE_BASES.format(user_id)
        return await RedisUtils.cache_delete(redis, key)
    
    @staticmethod
    async def set_knowledge_base_notes(
        redis: Redis, 
        knowledge_base_id: int, 
        page: int,
        notes_data: dict,
        expire: int = 300
    ) -> bool:
        """设置知识库笔记列表缓存
        
        Args:
            redis: Redis连接
            knowledge_base_id: 知识库ID
            page: 页码
            notes_data: 笔记列表数据，包含分页信息
            expire: 过期时间(秒)，默认5分钟
        """
        key = RedisCacheKey.KNOWLEDGE_BASE_NOTES.format(knowledge_base_id, page)
        return await RedisUtils.cache_set(redis, key, json.dumps(notes_data), expire=expire)
    
    @staticmethod
    async def get_knowledge_base_notes(redis: Redis, knowledge_base_id: int, page: int) -> Optional[dict]:
        """获取知识库笔记列表缓存"""
        key = RedisCacheKey.KNOWLEDGE_BASE_NOTES.format(knowledge_base_id, page)
        data = await RedisUtils.cache_get(redis, key)
        return json.loads(data) if data else None
    
    @staticmethod
    async def delete_knowledge_base_notes(redis: Redis, knowledge_base_id: int) -> None:
        """删除知识库所有笔记列表缓存（当知识库内容变更时调用）"""
        # 由于不知道具体有多少页，我们删除前10页的缓存
        for page in range(1, 11):
            key = RedisCacheKey.KNOWLEDGE_BASE_NOTES.format(knowledge_base_id, page)
            await RedisUtils.cache_delete(redis, key)
    
    @staticmethod
    async def clear_knowledge_base_cache(redis: Redis, user_id: int, knowledge_base_id: int) -> None:
        """清除知识库相关的所有缓存"""
        await RedisCache.delete_knowledge_bases(redis, user_id)
        await RedisCache.delete_knowledge_base_notes(redis, knowledge_base_id)
        await RedisCache.delete_user_notes(redis, user_id) 