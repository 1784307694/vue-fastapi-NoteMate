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


        # 数据库配置
    TORTOISE_ORM: dict = {
        "connections": {
            # SQLite配置
            # "sqlite": {
            #     "engine": "tortoise.backends.sqlite",
            #     "credentials": {"file_path": f"{BASE_DIR}/db.sqlite3"},
            # },
            
            # MySQL配置
            "mysql": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": "xiaocaibao.cn",
                    "port": 3306,
                    "user": "root",
                    "password": "HUANGxun1114",
                    "database": "test",
                },
            },

            # PostgreSQL配置（已注释）
            # "postgres": {
            #     "engine": "tortoise.backends.asyncpg",
            #     "credentials": {
            #         "host": "localhost",
            #         "port": 5432,
            #         "user": "yourusername",
            #         "password": "yourpassword",
            #         "database": "yourdatabase",
            #     },
            # },

            # MSSQL/Oracle配置（已注释）
            # "oracle": {
            #     "engine": "tortoise.backends.asyncodbc",
            #     "credentials": {...},
            # },

            # SQLServer配置（已注释）
            # "sqlserver": {
            #     "engine": "tortoise.backends.asyncodbc",
            #     "credentials": {...},
            # },
        },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],  # 模型路径
                "default_connection": "sqlite",             # 默认连接
            },
        },
        "use_tz": False,                    # 是否使用时区
        "timezone": "Asia/Shanghai",        # 时区设置
    }



settings = Settings()
