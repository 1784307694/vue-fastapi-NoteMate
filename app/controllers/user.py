from datetime import datetime
from typing import List, Optional

from fastapi.exceptions import HTTPException

from app.core.crud import CRUDBase
from app.models.admin import User
from app.schemas.login import CredentialsSchema
from app.schemas.users import UserCreate, UserUpdate
from app.utils.password import get_password_hash, verify_password

from .role import role_controller


class UserController(CRUDBase[User, UserCreate, UserUpdate]):
    """
    用户控制器类
    继承自CRUDBase,实现用户相关的业务逻辑
    
    泛型参数:
        User: 用户模型类
        UserCreate: 用户创建模型
        UserUpdate: 用户更新模型
    """
    def __init__(self):
        """初始化用户控制器,设置操作的模型为User"""
        super().__init__(model=User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱查找用户
        
        Args:
            email: 用户邮箱
            
        Returns:
            Optional[User]: 返回用户对象,不存在则返回None
        """
        return await self.model.filter(email=email).first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        通过用户名查找用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 返回用户对象,不存在则返回None
        """
        return await self.model.filter(username=username).first()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """
        通过手机号查找用户
        
        Args:
            phone: 用户手机号
            
        Returns:
            Optional[User]: 返回用户对象,不存在则返回None
        """
        return await self.model.filter(phone=phone).first()

    async def create_user(self, obj_in: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            obj_in: 用户创建模型实例
            
        Returns:
            User: 创建的用户对象
            
        说明:
            - 对密码进行哈希处理后再存储
        """
        obj_in.password = get_password_hash(password=obj_in.password)
        obj = await self.create(obj_in)
        return obj

    async def update_last_login(self, id: int) -> None:
        """
        更新用户最后登录时间
        
        Args:
            id: 用户ID
            
        说明:
            - 将最后登录时间更新为当前时间
        """
        user = await self.model.get(id=id)
        user.last_login = datetime.now()
        await user.save()

    async def authenticate(self, credentials: CredentialsSchema) -> Optional["User"]:
        """
        用户认证
        
        Args:
            credentials: 包含用户名和密码的凭证模型
            
        Returns:
            User: 认证成功的用户对象
            
        Raises:
            HTTPException: 认证失败时抛出相应的异常
            - 400: 用户名无效
            - 400: 密码错误
            - 400: 用户已被禁用
        """
        # 用户名登陆
        if credentials.loginType == "username":
            # 查找用户
            user = await self.model.filter(username=credentials.username).first()

            if not user:
                raise HTTPException(status_code=400, detail="无效的用户名")
            
            # 验证密码
            verified = verify_password(credentials.password, user.password)
            if not verified:
                raise HTTPException(status_code=400, detail="密码错误!")
                
            # 检查用户状态
            if not user.is_active:
                raise HTTPException(status_code=400, detail="用户已被禁用")
                
            return user
        
        # 邮箱登陆
        if credentials.loginType == "email":
            user = await self.model.filter(email=credentials.email).first()
            if not user:
                raise HTTPException(status_code=400, detail="无效的邮箱")
            
            # 验证密码
            verified = verify_password(credentials.password, user.password)
            if not verified:
                raise HTTPException(status_code=400, detail="密码错误!")
                
            # 检查用户状态
            if not user.is_active:
                raise HTTPException(status_code=400, detail="用户已被禁用")

            return user
        
        # 手机号登陆
        if credentials.loginType == "sms":
            return
            


    async def update_roles(self, user: User, role_ids: List[int]) -> None:
        """
        更新用户角色
        
        Args:
            user: 用户对象
            role_ids: 角色ID列表
            
        说明:
            - 清除用户现有角色
            - 添加新的角色关联
        """
        # 清除现有角色
        await user.roles.clear()
        # 添加新角色
        for role_id in role_ids:
            role_obj = await role_controller.get(id=role_id)
            await user.roles.add(role_obj)

    async def reset_password(self, user_id: int):
        """
        重置用户密码
        
        Args:
            user_id: 用户ID
            
        Raises:
            HTTPException: 
                403: 尝试重置超级管理员密码时抛出
                
        说明:
            - 将密码重置为"123456"
            - 不允许重置超级管理员密码
        """
        user_obj = await self.get(id=user_id)
        if user_obj.is_superuser:
            raise HTTPException(status_code=403, detail="不允许重置超级管理员密码")
        # 重置为默认密码"123456"
        user_obj.password = get_password_hash(password="123456")
        await user_obj.save()


# 创建用户控制器实例
user_controller = UserController()
