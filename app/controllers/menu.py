from typing import Optional

from app.core.crud import CRUDBase
from app.models.admin import Menu
from app.schemas.menus import MenuCreate, MenuUpdate


class MenuController(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    """
    菜单控制器类
    继承自CRUDBase,实现菜单相关的业务逻辑
    
    泛型参数:
        Menu: 菜单模型类
        MenuCreate: 菜单创建模型
        MenuUpdate: 菜单更新模型
        
    说明:
        - 负责处理系统菜单的CRUD操作
        - 提供菜单路径查询功能
    """
    def __init__(self):
        """
        初始化菜单控制器
        设置操作的模型为Menu
        """
        super().__init__(model=Menu)

    async def get_by_menu_path(self, path: str) -> Optional["Menu"]:
        """
        通过菜单路径获取菜单对象
        
        Args:
            path: 菜单路径
            
        Returns:
            Optional[Menu]: 返回匹配的菜单对象,如果不存在则返回None
            
        说明:
            - 用于根据前端路由路径查找对应的菜单配置
            - 路径匹配是精确匹配
        """
        return await self.model.filter(path=path).first()


# 创建菜单控制器实例
menu_controller = MenuController()
