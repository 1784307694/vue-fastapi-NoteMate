from enum import Enum, StrEnum


class EnumBase(Enum):
    """
    自定义枚举基类,扩展了标准Enum类的功能
    提供了获取枚举值和名称的便捷方法
    """
    
    @classmethod
    def get_member_values(cls):
        """获取所有枚举成员的值"""
        return [item.value for item in cls._member_map_.values()]

    @classmethod
    def get_member_names(cls):
        """获取所有枚举成员的名称"""
        return [name for name in cls._member_names_]


class MethodType(StrEnum):
    """
    HTTP请求方法枚举
    继承自StrEnum,确保所有值都是字符串类型
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    
class AccountStatus(StrEnum):
    NORMAL = "NORMAL"  # 正常
    FROZEN = "FROZEN"  # 冻结
    BLOCKED = "BLOCKED"  # 封锁
    CANCELLED = "CANCELLED"  # 注销

    
class FlowDirection(StrEnum):
    IN = "IN"  # 收入
    OUT = "OUT"  # 支出


class MenuType(StrEnum):
    """菜单类型枚举"""
    CATALOG = "catalog"  # 目录
    MENU = "menu"  # 菜单
    
class TradeType(StrEnum):
    """交易类型枚举"""
    DEPOSIT = "DEPOSIT"      # 充值
    WITHDRAW = "WITHDRAW"    # 提现
    TRANSFER = "TRANSFER"    # 转账(用户间交易)
    REFUND = "REFUND"       # 退款
    ADJUST = "ADJUST"       # 系统调账
    REWARD = "REWARD"       # 奖励发放
    FINE = "FINE"          # 罚款扣除
    
    
class OrderStatus(StrEnum):
    """订单状态枚举"""
    PENDING = "PENDING"  # 待支付
    PAID = "PAID"      # 已支付
    CANCELLED = "CANCELLED"  # 已取消
    FAILED = "FAILED"  # 支付失败
    REFUNDED = "REFUNDED"  # 已退款


class ChannelType(StrEnum):
    """支付渠道类型枚举"""
    ALIPAY = "ALIPAY"  # 支付宝
    WECHAT = "WECHAT"  # 微信