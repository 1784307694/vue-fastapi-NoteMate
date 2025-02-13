from typing import List

from app.core.crud import CRUDBase
from app.models.admin import Api, Menu, Role
from app.schemas.roles import RoleCreate, RoleUpdate


class RoleController(CRUDBase[Role, RoleCreate, RoleUpdate]):
    """
    角色控制器类
    继承自CRUDBase,实现角色相关的业务逻辑
    
    泛型参数:
        Role: 角色模型类
        RoleCreate: 角色创建模型
        RoleUpdate: 角色更新模型
    """
    def __init__(self):
        """初始化角色控制器,设置操作的模型为Role"""
        super().__init__(model=Role)

    async def is_exist(self, name: str) -> bool:
        """
        检查角色名称是否已存在
        
        Args:
            name: 角色名称
            
        Returns:
            bool: 如果角色名已存在返回True,否则返回False
        """
        return await self.model.filter(name=name).exists()

    async def update_roles(self, role: Role, menu_ids: List[int], api_infos: List[dict]) -> None:
        """
        更新角色的菜单和API权限
        
        Args:
            role: 角色对象
            menu_ids: 菜单ID列表
            api_infos: API信息列表,每个元素为包含path和method的字典
            
        说明:
            - 清除并重新设置角色的菜单权限
            - 清除并重新设置角色的API权限
            - api_infos中每个字典需包含path和method字段
        """
        # 清除并更新菜单权限
        await role.menus.clear()
        for menu_id in menu_ids:
            menu_obj = await Menu.filter(id=menu_id).first()
            await role.menus.add(menu_obj)

        # 清除并更新API权限
        await role.apis.clear()
        for item in api_infos:
            api_obj = await Api.filter(path=item.get("path"), method=item.get("method")).first()
            await role.apis.add(api_obj)


# 创建角色控制器实例
role_controller = RoleController()
