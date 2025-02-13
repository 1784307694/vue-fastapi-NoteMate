"""
账户相关的数据模型定义

包含以下模型:
- BaseAccount: 账户基础模型, 用于账户信息的展示
- AccountFlow: 账户流水模型, 用于记录账户资金变动
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class BaseAccount(BaseModel):
    """账户基础模型
    
    用于账户信息的展示, 包含账户的所有基础字段
    
    Attributes:
        id: 账户ID
        user_id: 用户ID
        balance: 账户余额
        frozen_amount: 冻结金额
        status: 账户状态
        created_at: 创建时间
        updated_at: 更新时间
    """
    id: int
    user_id: int
    balance: Decimal
    frozen_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime


class AccountFlow(BaseModel):
    """账户流水模型
    
    用于记录账户资金变动的详细信息
    
    Attributes:
        id: 流水ID
        account_id: 账户ID
        user_id: 用户ID
        order_no: 关联订单号
        amount: 变动金额
        balance: 变动后余额
        flow_type: 流水类型
        direction: 资金方向(IN-收入 OUT-支出)
        remark: 流水备注(可选)
        created_at: 创建时间
    """
    id: int
    account_id: int
    user_id: int
    order_no: str
    amount: Decimal
    balance: Decimal
    flow_type: str
    direction: str
    remark: Optional[str]
    created_at: datetime 