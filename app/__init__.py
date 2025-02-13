from app.core.dependency import RedisControl, MongoDBControl
from app.core.exceptions import SettingNotFound

from contextlib import asynccontextmanager  # 异步上下文管理器
from fastapi import FastAPI                 # FastAPI 框架
from tortoise import Tortoise              # ORM 数据库框架

# 导入自定义的初始化函数
from app.core.init_app import (
    init_data,            # 初始化数据
    make_middlewares,     # 创建中间件
    register_exceptions,  # 注册异常处理
    register_routers,     # 注册路由
)

try:
    from app.core.config import settings  # 加载应用配置
except ImportError:
    raise SettingNotFound("Can not import settings")  # 配置文件不存在时报错



@asynccontextmanager
async def lifespan(app: FastAPI):          # 应用生命周期管理
    await init_data()                      # 启动时：初始化数据
    yield                                  # 应用运行阶段
    await Tortoise.close_connections()     # 关闭时：清理数据库连接
    await RedisControl.close_pool()         # 关闭时：清理Redis连接
    await MongoDBControl.close_pool()      # 关闭时：清理MongoDB连接
    


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,          # API 文档标题
        description=settings.APP_DESCRIPTION, # API 文档描述
        version=settings.VERSION,           # API 版本
        openapi_url="/openapi.json",       # OpenAPI 文档地址
        middleware=make_middlewares(),      # 中间件配置
        lifespan=lifespan,                 # 生命周期管理器
    )
    register_exceptions(app)               # 注册异常处理器
    register_routers(app, prefix="/api")   # 注册路由（所有API以/api开头）
    return app


app = create_app()