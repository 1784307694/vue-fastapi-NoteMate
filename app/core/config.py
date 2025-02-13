import os
import typing

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    使用pydantic_settings进行配置管理和类型验证
    """
    # 基本应用信息
    VERSION: str = "0.1.0"                    # 应用版本号
    APP_TITLE: str = "notemate"      # 应用标题
    PROJECT_NAME: str = "notemate"   # 项目名称
    APP_DESCRIPTION: str = "Description"      # 应用描述

    # CORS（跨域资源共享）配置
    CORS_ORIGINS: typing.List = ["*"]         # 允许的源，"*"表示允许所有
    CORS_ALLOW_CREDENTIALS: bool = True       # 允许携带凭证
    CORS_ALLOW_METHODS: typing.List = ["*"]   # 允许的HTTP方法
    CORS_ALLOW_HEADERS: typing.List = ["*"]   # 允许的HTTP头

    # 调试模式
    DEBUG: bool = True 

    # 路径配置
    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))  # 项目根目录
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))                   # 基础目录
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")                                      # 日志目录 
    
    # 安全配置
    SECRET_KEY: str = "3488a63e1765035d386f05409663f55c83bfae3b3c61a932744b20ad14244dcf"  # JWT密钥
    JWT_ALGORITHM: str = "HS256"              # JWT加密算法
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # Token过期时间（7天）


    # redis配置
    REDIS_HOST: str = "xiaocaibao.cn"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = "HUANGxun1114"
    REDIS_ENCODING: str = "utf-8"
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_MAX_CONNECTIONS: int = 10000
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_URL: str = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # 日期时间格式
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"  # 日期时间格式化字符串


        # 数据库配置
    TORTOISE_ORM: dict = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": "xiaocaibao.cn",
                    "port": 3306,
                    "user": "root",
                    "password": "HUANGxun1114",
                    "database": "test",
                },
            },
        },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
                "default_connection": "default",
            },
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }
    
    # MongoDB配置
    MONGODB_HOST: str = "xiaocaibao.cn"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = "xiaocaibao"  # MongoDB用户名
    MONGODB_PASSWORD: str = "HUANGxun1114"  # MongoDB密码
    MONGODB_DB_NAME: str = "test"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    MONGODB_MAX_IDLE_TIME_MS: int = 10000
    # 构建MongoDB连接URL
    MONGODB_URL: str = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/"


    # 邮件配置
    SMTP_SERVER: str = "smtp.126.com"  # SMTP 服务器地址
    SMTP_PORT: int = 465  # SMTP 端口（通常是 587 或 465）
    SMTP_USERNAME: str = "a1784307694@126.com"  # 发件人邮箱
    SMTP_PASSWORD: str = "YPq5b3AEa6hgg8UZ"  # 发件人邮箱密码



settings = Settings()
