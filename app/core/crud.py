from typing import Any, Dict, Generic, List, NewType, Tuple, Type, TypeVar, Union

from pydantic import BaseModel
from tortoise.expressions import Q
from tortoise.models import Model

from app.log import logger

Total = NewType("Total", int)
ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用CRUD操作的基类
    
    泛型参数:
        ModelType: 数据库模型类型
        CreateSchemaType: 创建数据的验证模型类型
        UpdateSchemaType: 更新数据的验证模型类型
    """
    def __init__(self, model: Type[ModelType]):
        """
        初始化CRUD操作类
        
        Args:
            model: 数据库模型类
        """
        self.model = model

    async def get(self, id: int) -> ModelType:
        """
        根据ID获取单个记录
        
        Args:
            id: 记录ID
            
        Returns:
            返回查询到的模型实例
        """
        return await self.model.get(id=id)

    async def list(
        self, 
        page: int,                  # 页码
        page_size: int,            # 每页大小
        search: Q = Q(),           # 查询条件，默认为空
        order: list = []           # 排序条件，默认为空
    ) -> Tuple[Total, List[ModelType]]:
        """
        获取分页列表数据
        
        Args:
            page: 当前页码
            page_size: 每页记录数
            search: 查询条件
            order: 排序条件
            
        Returns:
            返回元组 (总记录数, 当前页数据列表)
        """
        query = self.model.filter(search)
        # 返回总数和分页数据
        # offset设置查询的偏移量，即跳过多少条记录
        return await query.count(), await query.offset((page - 1) * page_size).limit(page_size).order_by(*order)

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录
        
        Args:
            obj_in: 创建对象的数据,可以是字典或Pydantic模型
            
        Returns:
            返回创建的模型实例
        """
        # 判断输入是否为字典类型
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            # 如果是Pydantic模型，转换为字典
            obj_dict = obj_in.model_dump()
        # 创建模型实例并保存
        obj = self.model(**obj_dict)
        await obj.save()
        return obj

    async def update(
        self, 
        id: int,                                           # 记录ID
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]    # 更新的数据
    ) -> ModelType:
        """
        更新现有记录
        
        Args:
            id: 要更新的记录ID
            obj_in: 更新的数据,可以是字典或Pydantic模型
            
        Returns:
            返回更新后的模型实例
        """
        # 判断输入是否为字典类型
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            # 如果是Pydantic模型，转换为字典，排除未设置的字段和id字段
            obj_dict = obj_in.model_dump(exclude_unset=True, exclude={"id"})
        # 获取现有记录
        obj = await self.get(id=id)
        # 更新记录并保存
        obj = obj.update_from_dict(obj_dict)
        await obj.save()
        return obj

    async def remove(self, id: int) -> None:
        """
        删除记录
        
        Args:
            id: 要删除的记录ID
        """
        # 获取要删除的记录
        obj = await self.get(id=id)
        # 执行删除操作
        await obj.delete()
