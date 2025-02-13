import asyncio
from datetime import datetime

from tortoise import fields, models

from app.core.config import settings


class BaseModel(models.Model):
    """
    基础模型类，所有数据模型的父类
    提供通用的字段和方法
    """
    # 主键字段，使用大整数类型，并创建索引
    id = fields.BigIntField(pk=True, index=True)

    async def to_dict(self, m2m: bool = False, exclude_fields: list[str] | None = None):
        """
        将模型实例转换为字典格式
        
        Args:
            m2m (bool): 是否包含多对多关系字段
            exclude_fields (list[str] | None): 需要排除的字段列表
        
        Returns:
            dict: 模型数据的字典表示
        """
        # 初始化排除字段列表
        if exclude_fields is None:
            exclude_fields = []

        # 处理普通字段
        d = {}
        for field in self._meta.db_fields:
            if field not in exclude_fields:
                value = getattr(self, field)
                # 格式化日期时间字段
                if isinstance(value, datetime):
                    value = value.strftime(settings.DATETIME_FORMAT)
                d[field] = value

        # 处理多对多关系字段
        if m2m:
            # 创建异步任务列表，获取所有多对多字段的值
            tasks = [
                self.__fetch_m2m_field(field, exclude_fields)
                for field in self._meta.m2m_fields
                if field not in exclude_fields
            ]
            # 并发执行所有任务
            results = await asyncio.gather(*tasks)
            # 将结果添加到返回字典中
            for field, values in results:
                d[field] = values

        return d

    async def __fetch_m2m_field(self, field, exclude_fields):
        """
        获取多对多关系字段的值
        
        Args:
            field (str): 字段名
            exclude_fields (list): 需要排除的字段列表
        
        Returns:
            tuple: (字段名, 格式化后的值列表)
        """
        # 获取关联的所有记录
        values = await getattr(self, field).all().values()
        formatted_values = []

        # 处理每条记录
        for value in values:
            formatted_value = {}
            for k, v in value.items():
                if k not in exclude_fields:
                    # 格式化日期时间字段
                    if isinstance(v, datetime):
                        formatted_value[k] = v.strftime(settings.DATETIME_FORMAT)
                    else:
                        formatted_value[k] = v
            formatted_values.append(formatted_value)

        return field, formatted_values

    class Meta:
        # 标记为抽象模型，不会创建实际的数据库表
        abstract = True


class UUIDModel:
    """
    UUID 模型混入类
    为模型添加 UUID 字段
    """
    # UUID字段，唯一且创建索引，但不作为主键
    uuid = fields.UUIDField(unique=True, pk=False, index=True)


class TimestampMixin:
    """
    时间戳混入类
    为模型添加创建时间和更新时间字段
    """
    # 创建时间，自动设置为创建记录的时间
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    # 更新时间，每次更新记录时自动更新
    updated_at = fields.DatetimeField(auto_now=True, index=True)
