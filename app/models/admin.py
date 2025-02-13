from tortoise import fields

from .enums import MethodType, MenuType, AccountStatus, FlowDirection, TradeType, OrderStatus, ChannelType
from .base import BaseModel, TimestampMixin




class User(BaseModel, TimestampMixin):
    """
    用户模型
    继承自BaseModel和TimestampMixin,包含基础字段和时间戳
    """
    # 基本信息字段
    username = fields.CharField(min_length=2, max_length=20, unique=True, description="用户名称", index=True)
    alias = fields.CharField(max_length=30, null=True, description="姓名", index=True)
    email = fields.CharField(max_length=255, null=True, description="邮箱", index=True)

    phone = fields.CharField(max_length=20, null=True, description="电话", index=True)
    password = fields.CharField(max_length=128, null=True, description="密码")
    avatar = fields.CharField(max_length=255, null=True, description="头像")
    bio = fields.TextField(null=True, description="个人简介")

    
    # 状态字段
    is_active = fields.BooleanField(default=True, description="是否激活", index=True)
    is_superuser = fields.BooleanField(default=False, description="是否为超级管理员", index=True)
    last_login = fields.DatetimeField(null=True, description="最后登录时间", index=True)
    
    # 关联字段
    roles = fields.ManyToManyField("models.Role", related_name="user_roles")  # 多对多关系：用户-角色

    class Meta:
        table = "user"


class UserFollow(BaseModel, TimestampMixin):
    """用户关注关系表"""
    user_id = fields.IntField(description="关注者ID", index=True)
    followed_id = fields.IntField(description="被关注者ID", index=True)
    
    class Meta:
        table = "user_follow"
        unique_together = ("user_id", "followed_id")


class Role(BaseModel, TimestampMixin):
    """
    角色模型
    用于权限管理,可以关联菜单和API权限
    """
    name = fields.CharField(max_length=20, unique=True, description="角色名称", index=True)
    desc = fields.CharField(max_length=500, null=True, description="角色描述")
    # 多对多关系
    menus = fields.ManyToManyField("models.Menu", related_name="role_menus")  # 角色-菜单
    apis = fields.ManyToManyField("models.Api", related_name="role_apis")     # 角色-API

    class Meta:
        table = "role"
        
        
class Api(BaseModel, TimestampMixin):
    """
    API模型
    记录系统中的API接口信息
    """
    path = fields.CharField(max_length=100, description="API路径", index=True)
    method = fields.CharEnumField(MethodType, description="请求方法", index=True)  # 使用MethodType枚举
    summary = fields.CharField(max_length=500, description="请求简介", index=True)
    tags = fields.CharField(max_length=100, description="API标签", index=True)

    class Meta:
        table = "api"


class Menu(BaseModel, TimestampMixin):
    """
    菜单模型
    系统的菜单结构,支持层级关系
    """
    name = fields.CharField(max_length=20, description="菜单名称", index=True)
    remark = fields.JSONField(null=True, description="保留字段")
    menu_type = fields.CharEnumField(MenuType, null=True, description="菜单类型")
    icon = fields.CharField(max_length=100, null=True, description="菜单图标")
    path = fields.CharField(max_length=100, description="菜单路径", index=True)
    order = fields.IntField(default=0, description="排序", index=True)
    parent_id = fields.IntField(default=0, max_length=10, description="父菜单ID", index=True)
    is_hidden = fields.BooleanField(default=False, description="是否隐藏")
    component = fields.CharField(max_length=100, description="组件")
    keepalive = fields.BooleanField(default=True, description="存活")
    redirect = fields.CharField(max_length=100, null=True, description="重定向")

    class Meta:
        table = "menu"
        

class KnowledgeBases(BaseModel, TimestampMixin):
    """知识库表"""
    user_id = fields.IntField(description="用户ID", index=True)
    name = fields.CharField(max_length=200, description="标题")
    type = fields.IntField(description="类型: 0-私有 1-公开", default=0)
    
    class Meta:
        table = "knowledge_bases"
    
    
        
class Note(BaseModel, TimestampMixin):
    """笔记表"""
    user_id = fields.IntField(description="作者ID", index=True)
    knowledge_bases_id = fields.IntField(description="知识库ID", index=True)
    title = fields.CharField(max_length=200, description="标题")
    cover = fields.CharField(max_length=255, null=True, description="封面")
    introduction = fields.TextField(null=True, description="简介")
    content = fields.TextField(null=True, description="内容")
    type = fields.IntField(description="类型: 0-免费 1-付费", default=0)
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="价格")
    status = fields.IntField(description="状态: 0-私有 1-公开 2-审核中", default=0)

    view_count = fields.IntField(default=0, description="浏览次数")
    like_count = fields.IntField(default=0, description="点赞次数")
    buy_count = fields.IntField(default=0, description="购买次数")
    
    
    class Meta:
        table = "note"


class NoteCollection(BaseModel, TimestampMixin):
    """笔记收藏表"""
    user_id = fields.IntField(description="用户ID", index=True)
    note_id = fields.IntField(description="笔记ID", index=True)
    
    class Meta:
        table = "note_collection"
        unique_together = ("user_id", "note_id")


class Account(BaseModel, TimestampMixin):
    """账户表 - 用户资金账户"""
    user_id = fields.IntField(description="用户ID", unique=True, index=True)
    balance = fields.DecimalField(max_digits=18, decimal_places=2, default=0, description="账户余额")
    frozen_amount = fields.DecimalField(max_digits=18, decimal_places=2, default=0, description="冻结金额")
    status = fields.CharEnumField(AccountStatus, default="NORMAL", description="账户状态", index=True)
    
    class Meta:
        table = "account"
        
        
class AccountFlow(BaseModel, TimestampMixin):
    """账户流水表"""
    account_id = fields.IntField(description="账户ID", index=True)
    user_id = fields.IntField(description="用户ID", index=True)
    order_no = fields.CharField(max_length=32, index=True, description="关联订单号")
    amount = fields.DecimalField(max_digits=18, decimal_places=2, description="变动金额")
    balance = fields.DecimalField(max_digits=18, decimal_places=2, description="变动后余额")
    flow_type = fields.CharEnumField(TradeType, description="流水类型", index=True)
    direction = fields.CharEnumField(FlowDirection, description="资金方向: IN-收入 OUT-支出", index=True)
    remark = fields.CharField(max_length=255, null=True, description="流水备注")
    
    class Meta:
        table = "account_flow"
        
        
class TradeOrder(BaseModel, TimestampMixin):
    """交易订单表"""
    order_no = fields.CharField(max_length=32, unique=True, description="订单号")
    user_id = fields.IntField(description="用户ID", index=True)
    account_id = fields.IntField(description="账户ID", index=True)
    # 新增字段
    target_user_id = fields.IntField(null=True, description="目标用户ID", index=True)  # 转账时的接收方
    target_account_id = fields.IntField(null=True, description="目标账户ID", index=True)  # 转账时的接收方账户
    amount = fields.DecimalField(max_digits=18, decimal_places=2, description="交易金额")
    channel_id = fields.IntField(description="支付渠道ID", index=True)
    
    trade_type = fields.CharEnumField(TradeType, description="交易类型", index=True)
    status = fields.CharEnumField(OrderStatus, description="订单状态", index=True)
    remark = fields.CharField(max_length=255, null=True, description="交易备注")
    complete_time = fields.DatetimeField(null=True, description="完成时间")
    
    product_id = fields.IntField(null=True, description="商品ID(笔记ID)", index=True)

class PayChannel(BaseModel, TimestampMixin):
    """支付渠道表"""
    name = fields.CharField(max_length=50, description="渠道名称")
    code = fields.CharField(max_length=50, unique=True, description="渠道编码")
    channel_type = fields.CharEnumField(ChannelType, description="渠道类型", index=True)
    config = fields.JSONField(description="渠道配置")
    is_active = fields.BooleanField(default=True, description="是否启用")
    
    class Meta:
        table = "pay_channel"
        


class Comment(BaseModel, TimestampMixin):
    """评论表"""
    note_id = fields.IntField(description="笔记ID", index=True)
    user_id = fields.IntField(description="评论用户ID", index=True)
    content = fields.TextField(description="评论内容")
    parent_id = fields.IntField(null=True, description="父评论ID", index=True)  # 支持回复功能
    like_count = fields.IntField(default=0, description="点赞数")
    root_id = fields.IntField(null=True, description="根评论ID", index=True)  # 用于快速获取评论树
    
    class Meta:
        table = "comment"



class AuditLog(BaseModel, TimestampMixin):
    """
    审计日志模型
    记录用户操作日志
    """
    ip = fields.CharField(max_length=64, null=True, description="IP地址")
    user_id = fields.IntField(description="用户ID", index=True)
    username = fields.CharField(max_length=64, default="", description="用户名称", index=True)
    module = fields.CharField(max_length=64, default="", description="功能模块", index=True)
    summary = fields.CharField(max_length=128, default="", description="请求描述", index=True)
    method = fields.CharField(max_length=10, default="", description="请求方法", index=True)
    path = fields.CharField(max_length=255, default="", description="请求路径", index=True)
    host = fields.CharField(max_length=255, default="", description="请求ip", index=True)
    status = fields.IntField(default=-1, description="状态码", index=True)
    response_time = fields.IntField(default=0, description="响应时间(单位ms)", index=True)
    