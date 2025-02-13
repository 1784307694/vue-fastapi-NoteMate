from typing import Optional, AsyncGenerator

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
import redis.asyncio as aioredis
from fastapi import Depends, Header, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.ctx import CTX_USER_ID
from app.models import Role, User
from app.core.config import settings
from app.log import logger


class AuthControl:
    """
    认证控制类
    处理用户身份验证和Token解析
    """
    @classmethod
    async def is_authed(cls, token: str = Header(..., description="token验证")) -> Optional["User"]:
        """
        验证用户是否已认证
        
        Args:
            token (str): HTTP请求头中的token
            
        Returns:
            Optional[User]: 认证成功返回用户对象
            
        Raises:
            HTTPException: 认证失败时抛出相应的异常
                - 401: Token无效或过期
                - 403: 用户未找到或被禁用
                - 500: 其他系统错误
        """
        try:
            # 开发模式：使用测试token
            if token == "dev":
                user = await User.filter().first()
                user_id = user.id
            else:
                # 正式环境：解析JWT token
                decode_data = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[settings.JWT_ALGORITHM]
                )
                user_id = decode_data.get("user_id")
            
            # 查找用户并验证
            user = await User.filter(id=user_id).first()
            if not user:
                raise HTTPException(status_code=403, detail="用户不存在")
                
            if not user.is_active:
                raise HTTPException(status_code=403, detail="用户已被禁用")
            
            # 设置上下文用户ID
            CTX_USER_ID.set(int(user_id))
            return user
            
        except ExpiredSignatureError:
            # Token已过期
            raise HTTPException(status_code=401, detail="Token已过期")
        except JWTError:
            # Token验证失败
            raise HTTPException(status_code=401, detail="无效的Token")
        except Exception as e:
            # 其他系统错误
            raise HTTPException(status_code=500, detail=f"系统错误: {str(e)}")


class PermissionControl:
    """
    权限控制类
    处理用户权限验证
    """
    @classmethod
    async def has_permission(
        cls, 
        request: Request, 
        current_user: User = Depends(AuthControl.is_authed)
    ) -> None:
        """
        验证用户是否有权限访问当前接口
        
        Args:
            request (Request): FastAPI请求对象
            current_user (User): 当前认证用户
            
        Raises:
            HTTPException: 权限验证失败时抛出异常
        """
        # 超级管理员跳过权限检查
        if current_user.is_superuser:
            return
            
        # 获取请求方法和路径
        method = request.method
        path = request.url.path
        
        # 获取用户角色
        roles: list[Role] = await current_user.roles
        if not roles:
            raise HTTPException(
                status_code=403, 
                detail="The user is not bound to a role"
            )
            
        # 获取角色的所有API权限
        apis = [await role.apis for role in roles]
        # 构建权限集合：(方法, 路径)元组的集合
        permission_apis = list(set(
            (api.method, api.path) for api in sum(apis, [])
        ))
        
        # 验证当前请求是否在权限范围内
        if (method, path) not in permission_apis:
            raise HTTPException(
                status_code=403, 
                detail=f"Permission denied method:{method} path:{path}"
            )
        

class RedisControl:
    """Redis连接池控制类 - 管理Redis连接池的生命周期"""
    
    _redis_pool = None  # Redis连接池单例
    
    @classmethod
    async def get_redis_pool(cls) -> aioredis.Redis:
        """
        获取Redis连接池(单例模式)
        
        Returns:
            aioredis.Redis: Redis连接池实例
        """
        if cls._redis_pool is None:
            # 创建新的连接池
            cls._redis_pool = aioredis.from_url(
                settings.REDIS_URL,                    # Redis连接URL
                encoding=settings.REDIS_ENCODING,      # 编码方式
                decode_responses=settings.REDIS_DECODE_RESPONSES,  # 是否自动解码响应
                max_connections=settings.REDIS_MAX_CONNECTIONS,    # 最大连接数
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,      # 套接字超时
                retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT  # 超时重试
            )
        return cls._redis_pool
        
    @classmethod
    async def get_redis(cls) -> AsyncGenerator[aioredis.Redis, None]:
        """
        Redis依赖注入函数 - 用于FastAPI依赖注入系统
        
        Yields:
            aioredis.Redis: Redis连接池实例
            
        Usage:
            @app.get("/")
            async def handler(redis: Redis = Depends(RedisControl.get_redis)):
                await redis.set("key", "value")
        """
        redis = await cls.get_redis_pool()
        try:
            yield redis  # 返回连接池实例
        finally:
            # 使用连接池不需要关闭单个连接
            pass

    @classmethod
    async def close_pool(cls) -> None:
        """
        关闭Redis连接池
        在应用关闭时调用此方法清理资源
        """
        if cls._redis_pool is not None:
            await cls._redis_pool.close()
            cls._redis_pool = None


class MongoDBControl:
    """MongoDB连接池控制类 - 管理MongoDB连接池的生命周期"""
    
    _mongo_client: Optional[AsyncIOMotorClient] = None  # MongoDB客户端单例
    _mongo_db: Optional[AsyncIOMotorDatabase] = None    # MongoDB数据库实例
    
    @classmethod
    async def get_mongo_pool(cls) -> AsyncIOMotorDatabase:
        """
        获取MongoDB连接池(单例模式)
        
        Returns:
            AsyncIOMotorDatabase: MongoDB数据库实例
        """
        if cls._mongo_client is None:
            # 创建新的连接池
            cls._mongo_client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                maxIdleTimeMS=settings.MONGODB_MAX_IDLE_TIME_MS,
                serverSelectionTimeoutMS=5000,    # 服务器选择超时
                connectTimeoutMS=10000,           # 连接超时
                socketTimeoutMS=10000,            # socket超时
                waitQueueTimeoutMS=5000           # 等待队列超时
            )
            cls._mongo_db = cls._mongo_client[settings.MONGODB_DB_NAME]
            
            # 测试连接
            try:
                await cls._mongo_client.admin.command('ping')
                logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error(f"MongoDB connection error: {e}")
                raise
                
        return cls._mongo_db
        
    @classmethod
    async def get_mongodb(cls) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
        """
        MongoDB依赖注入函数 - 用于FastAPI依赖注入系统
        
        Yields:
            AsyncIOMotorDatabase: MongoDB数据库实例
            
        Usage:
            @app.get("/")
            async def handler(mongodb: AsyncIOMotorDatabase = DependMongoDB):
                await mongodb.collection.find_one({"key": "value"})
        """
        db = await cls.get_mongo_pool()
        try:
            yield db
        finally:
            # 使用连接池不需要关闭单个连接
            pass

    @classmethod
    async def close_pool(cls) -> None:
        """
        关闭MongoDB连接池
        在应用关闭时调用此方法清理资源
        """
        if cls._mongo_client is not None:
            cls._mongo_client.close()
            cls._mongo_client = None
            cls._mongo_db = None
            logger.info("MongoDB connection pool closed")


# 依赖注入快捷方式
DependAuth = Depends(AuthControl.is_authed)  # 仅认证
DependPermisson = Depends(PermissionControl.has_permission)  # 认证+权限
DependRedis = Depends(RedisControl.get_redis)  # Redis依赖
DependMongoDB = Depends(MongoDBControl.get_mongodb)