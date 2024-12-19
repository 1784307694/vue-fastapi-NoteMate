"""
配置文件
包含应用程序的所有配置项
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NoteMate"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key"  # 在生产环境中应该使用环境变量
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True

settings = Settings() 