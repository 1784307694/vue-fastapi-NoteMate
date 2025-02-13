"""
API控制器模块

提供API相关的业务逻辑处理, 包括:
- API的基本CRUD操作
- API列表的自动刷新功能
"""

from fastapi.routing import APIRoute

from app.core.crud import CRUDBase
from app.log import logger
from app.models.admin import Api
from app.schemas.apis import ApiCreate, ApiUpdate


class ApiController(CRUDBase[Api, ApiCreate, ApiUpdate]):
    """API控制器类
    
    继承自CRUDBase, 提供API的基本CRUD操作和特殊业务逻辑
    
    Attributes:
        model: API数据模型类
    """
    
    def __init__(self):
        """初始化API控制器
        
        设置数据模型为Api
        """
        super().__init__(model=Api)

    async def refresh_api(self):
        """刷新API列表
        
        自动扫描所有路由, 更新API数据:
        1. 删除已不存在的API记录
        2. 更新已存在的API信息
        3. 创建新的API记录
        
        Note:
            - 只处理带有鉴权的API路由
            - 通过比对路由方法和路径判断API是否存在
        """
        from app import app

        # 删除废弃API数据
        all_api_list = []
        for route in app.routes:
            # 只更新有鉴权的API
            if isinstance(route, APIRoute) and len(route.dependencies) > 0:
                all_api_list.append((list(route.methods)[0], route.path_format))
        
        # 删除不存在的API记录
        delete_api = []
        for api in await Api.all():
            if (api.method, api.path) not in all_api_list:
                delete_api.append((api.method, api.path))
        for item in delete_api:
            method, path = item
            logger.debug(f"API Deleted {method} {path}")
            await Api.filter(method=method, path=path).delete()

        # 更新或创建API记录
        for route in app.routes:
            if isinstance(route, APIRoute) and len(route.dependencies) > 0:
                method = list(route.methods)[0]
                path = route.path_format
                summary = route.summary
                tags = list(route.tags)[0]
                
                # 检查API是否存在
                api_obj = await Api.filter(method=method, path=path).first()
                if api_obj:
                    # 更新已存在的API
                    await api_obj.update_from_dict(dict(
                        method=method,
                        path=path,
                        summary=summary,
                        tags=tags
                    )).save()
                else:
                    # 创建新的API
                    logger.debug(f"API Created {method} {path}")
                    await Api.create(**dict(
                        method=method,
                        path=path,
                        summary=summary,
                        tags=tags
                    ))


# 创建API控制器实例
api_controller = ApiController()
