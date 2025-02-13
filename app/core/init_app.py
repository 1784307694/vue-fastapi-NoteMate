import shutil

from aerich import Command
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.expressions import Q


from app.api import api_router
from app.controllers.api import api_controller
from app.controllers.user import UserCreate, user_controller
from app.core.exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
)
from app.log import logger
from app.models.admin import Api, Menu, Role
from app.models.enums import MenuType
from app.core.config import settings

from .middlewares import BackGroundTaskMiddleware, HttpAuditLogMiddleware



def register_routers(app: FastAPI, prefix: str = "/api"):
    """注册API路由"""
    app.include_router(api_router, prefix=prefix)  # 注册路由,添加前缀


def make_middlewares():
    """配置中间件列表"""
    middleware = [
        # CORS中间件：处理跨域请求
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,          # 允许的源
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,  # 允许携带凭证
            allow_methods=settings.CORS_ALLOW_METHODS,    # 允许的HTTP方法
            allow_headers=settings.CORS_ALLOW_HEADERS,    # 允许的请求头
        ),
        # 后台任务中间件：处理异步任务
        Middleware(BackGroundTaskMiddleware),
        # HTTP审计日志中间件：记录请求日志
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],  # 需要记录的HTTP方法
            exclude_paths=["/docs", "/openapi.json"],  # 排除的路径
        ),
    ]
    return middleware



def register_exceptions(app: FastAPI):
    """注册全局异常处理器"""
    # 注册各种异常的处理函数
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)  # 数据不存在异常
    app.add_exception_handler(HTTPException, HttpExcHandle)      # HTTP异常
    app.add_exception_handler(IntegrityError, IntegrityHandle)  # 数据完整性异常
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)   # 请求验证异常
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle) # 响应验证异常



# 以下是数据初始化

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

async def init_menus():
    """初始化系统菜单"""
    # 检查是否已存在菜单
    menus = await Menu.exists()
    if not menus:
        # 创建父级菜单：系统管理
        parent_menu = await Menu.create(
            menu_type=MenuType.CATALOG,  # 菜单类型：目录
            name="系统管理",
            path="/system",
            order=1,                     # 排序序号
            parent_id=0,                 # 父级ID为0表示顶级菜单
            icon="Setting",              # 菜单图标
            is_hidden=False,             # 是否隐藏
            component="Layout",          # 组件
            keepalive=False,             # 是否保持存活
            redirect="/system/user",     # 重定向路径
        )
        
        # 创建子菜单列表
        children_menu = [
            # 用户管理菜单
            Menu(
                menu_type=MenuType.MENU,
                name="用户管理",
                path="user",
                order=1,
                parent_id=parent_menu.id,
                icon="User",
                is_hidden=False,
                component="/system/user",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="角色管理",
                path="role",
                order=2,
                parent_id=parent_menu.id,
                icon="UserFilled",
                is_hidden=False,
                component="/system/role",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="菜单管理",
                path="menu",
                order=3,
                parent_id=parent_menu.id,
                icon="List",
                is_hidden=False,
                component="/system/menu",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="API管理",
                path="api",
                order=4,
                parent_id=parent_menu.id,
                icon="Connection",
                is_hidden=False,
                component="/system/api",
                keepalive=False,
            ),
            # Menu(
            #     menu_type=MenuType.MENU,
            #     name="部门管理",
            #     path="dept",
            #     order=5,
            #     parent_id=parent_menu.id,
            #     icon="mingcute:department-line",
            #     is_hidden=False,
            #     component="/system/dept",
            #     keepalive=False,
            # ),
            Menu(
                menu_type=MenuType.MENU,
                name="审计日志",
                path="auditlog",
                order=6,
                parent_id=parent_menu.id,
                icon="Document",
                is_hidden=False,
                component="/system/auditlog",
                keepalive=False,
            ),
        ]
        # 批量创建子菜单
        await Menu.bulk_create(children_menu)
        
        # 创建一级菜单示例
        await Menu.create(
            menu_type=MenuType.MENU,
            name="一级菜单",
            path="/top-menu",
            order=2,
            parent_id=0,
            icon="material-symbols:featured-play-list-outline",
            is_hidden=False,
            component="/top-menu",
            keepalive=False,
            redirect="",
        )

async def init_roles():
    """初始化角色"""
    # 检查是否已存在角色
    roles = await Role.exists()
    if not roles:
        # 创建管理员角色
        admin_role = await Role.create(
            name="管理员",
            desc="管理员角色",
        )
        # 创建普通用户角色
        user_role = await Role.create(
            name="普通用户",
            desc="普通用户角色",
        )

        # 分配所有API给管理员角色
        all_apis = await Api.all()
        await admin_role.apis.add(*all_apis)
        
        # 分配所有菜单给管理员
        all_menus = await Menu.all()
        await admin_role.menus.add(*all_menus)

        # 为普通用户分配基本API(GET方法和基础模块)
        basic_apis = await Api.filter(Q(method__in=["GET"]) | Q(tags="基础模块"))
        await user_role.apis.add(*basic_apis)
        
        
async def init_apis():
    """初始化API列表"""
    # 检查是否已存在API
    apis = await api_controller.model.exists()
    if not apis:
        # 刷新API列表
        await api_controller.refresh_api()



async def init_data():
    """系统初始化主函数"""
    # 按顺序执行初始化操作
    await init_db();           # 初始化数据库
    await init_menus()
    await init_roles()
    await init_apis()
    
