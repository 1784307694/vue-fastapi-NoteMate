import shutil

from fastapi import FastAPI
from aerich import Command

from app.api import api_router
from app.core.config import settings
from app.log import logger

def register_routers(app: FastAPI, prefix: str = "/api"):
    """注册API路由"""
    app.include_router(api_router, prefix=prefix)  # 注册路由,添加前缀


















async def init_db():
    """初始化数据库"""
    # 创建数据库迁移命令对象
    command = Command(tortoise_config=settings.TORTOISE_ORM)
    try:
        # 初始化数据库
        await command.init_db(safe=True)
    except FileExistsError:
        pass

    # 初始化迁移
    await command.init()
    try:
        # 执行迁移
        await command.migrate()
    except AttributeError:
        # 如果获取模型历史失败,重新初始化
        logger.warning("unable to retrieve model history from database, model history will be created from scratch")
        shutil.rmtree("migrations")
        await command.init_db(safe=True)

    # 升级数据库
    await command.upgrade(run_in_transaction=True)

