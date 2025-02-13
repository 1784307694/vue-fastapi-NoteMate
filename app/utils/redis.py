from typing import Any, Optional
import json
from redis.asyncio import Redis

class RedisUtils:
    """Redis工具类 - 提供Redis缓存操作的高级封装"""
    
    @staticmethod
    async def cache_set(
        redis: Redis,        # Redis客户端实例
        key: str,           # 缓存键名
        value: Any,         # 要缓存的值(任意类型)
        expire: int = 3600  # 过期时间(秒),默认1小时
    ) -> bool:
        """
        设置缓存
        
        Args:
            redis: Redis客户端实例
            key: 缓存键名
            value: 要缓存的值(会被JSON序列化)
            expire: 过期时间(秒)
            
        Returns:
            bool: 设置成功返回True,失败返回False
        """
        try:
            value_str = json.dumps(value)  # 将值序列化为JSON字符串
            await redis.set(key, value_str, ex=expire)  # 设置键值对和过期时间
            return True
        except Exception:
            return False

    @staticmethod
    async def cache_get(
        redis: Redis,        # Redis客户端实例
        key: str,           # 缓存键名
        default: Any = None # 默认返回值
    ) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            redis: Redis客户端实例
            key: 缓存键名
            default: 获取失败时的默认返回值
            
        Returns:
            Optional[Any]: 返回缓存的值(JSON反序列化后)或默认值
        """
        try:
            value = await redis.get(key)  # 获取缓存值
            if not value:
                return default
            try:
                # 尝试 JSON 反序列化
                return json.loads(value)
            except json.JSONDecodeError:
                # 如果不是 JSON 格式，直接返回字符串
                return value.decode() if isinstance(value, bytes) else value
        except Exception:
            return default
        
    @staticmethod
    async def cache_delete(
        redis: Redis,
        key: str
    ) -> bool:
        """
        删除缓存
        
        Args:
            redis: Redis客户端实例
            key: 缓存键名
            
        Returns:
            bool: 删除成功返回True,失败返回False
        """
        try:
            await redis.delete(key)
            return True
        except Exception:
            return False    
