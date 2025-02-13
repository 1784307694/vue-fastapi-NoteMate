"""
交易相关的数据模型定义

包含以下模型:
- BaseOrder: 订单基础模型, 用于订单信息的展示
- OrderCreate: 订单创建模型, 用于创建新订单
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class BaseOrder(BaseModel):
    """订单基础模型
    
    用于订单信息的展示, 包含订单的所有基础字段
    
    Attributes:
        id: 订单ID
        order_no: 订单号
        user_id: 用户ID
        account_id: 账户ID
        target_user_id: 目标用户ID(转账场景)
        target_account_id: 目标账户ID(转账场景)
        amount: 交易金额
        channel_id: 支付渠道ID
        trade_type: 交易类型
        status: 订单状态
        product_id: 商品ID(笔记ID)
        remark: 交易备注
        complete_time: 完成时间
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    order_no: str
    user_id: int
    account_id: int
    target_user_id: Optional[int]
    target_account_id: Optional[int]
    amount: Decimal
    channel_id: int
    trade_type: str
    status: str
    product_id: Optional[int]
    remark: Optional[str]
    complete_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class OrderCreate(BaseModel):
    """订单创建模型
    
    用于创建新订单时的数据验证
    
    Attributes:
        amount: 交易金额
        channel_id: 支付渠道ID
        trade_type: 交易类型
        product_id: 商品ID(笔记ID, 可选)
        remark: 交易备注(可选)
    """
    amount: Decimal = Field(description="交易金额")
    channel_id: int = Field(description="支付渠道ID")
    trade_type: str = Field(description="交易类型")
    product_id: Optional[int] = Field(description="商品ID(笔记ID)")
    remark: Optional[str] = Field(description="交易备注") 