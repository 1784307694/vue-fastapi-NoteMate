# 在线笔记系统设计方案

## 1. 技术栈选择

### 前端
- 框架: Vue3
- UI组件库: Element Plus
- Markdown编辑器: v-md-editor
- HTTP客户端: Axios
- 状态管理: Pinia
- 路由: Vue Router

### 后端
- 框架: FastAPI
- ORM: Tortoise-ORM (MySQL), Motor/PyMongo (MongoDB)
- 缓存: Redis
- 认证: JWT
- 异步框架: uvicorn

### 数据存储
- 关系型数据库: MySQL (用户信息、交易数据)
- 文档数据库: MongoDB (笔记内容)
- 缓存数据库: Redis (会话信息、验证码、热点数据)

## 2. 数据库设计

### MySQL 模型设计 (Tortoise-ORM)

```python

```

### MongoDB 集合设计

#### 笔记集合(notes)
```javascript
{
  _id: ObjectId,
  user_id: Long,  // 关联MySQL用户ID
  title: String,
  content: String,  // Markdown内容
  type: Number,    // 0-免费 1-付费
  price: Decimal128,
  status: Number,  // 0-私有 1-公开 2-审核中
  view_count: Number,
  like_count: Number,
  tags: [String],
  created_at: ISODate,
  updated_at: ISODate
}
```

### Redis 缓存设计
```
# 用户Token
user:token:{user_id} -> JWT Token

# 验证码
sms:code:{phone} -> code
expire: 5min

# 笔记访问计数
note:views:{note_id} -> count
expire: 1day

# 热门笔记列表
hot:notes -> Sorted Set of note_ids
expire: 1hour
```

## 3. API设计

### 用户模块
```
POST /api/v1/user/register - 用户注册
POST /api/v1/user/login - 用户登录
POST /api/v1/user/sms/send - 发送验证码
GET /api/v1/user/info - 获取用户信息
PUT /api/v1/user/info - 修改用户信息
```

### 笔记模块
```
POST /api/v1/notes - 创建笔记
PUT /api/v1/notes/{id} - 修改笔记
GET /api/v1/notes/{id} - 获取笔记详情
GET /api/v1/notes - 获取笔记列表
POST /api/v1/notes/{id}/purchase - 购买笔记
```

### 交易模块
```
POST /api/v1/transactions/recharge - 用户充值
GET /api/v1/transactions - 交易记录列表
POST /api/v1/payments/callback - 支付回调
```

### 管理后台
```
GET /api/v1/admin/notes - 笔记管理
PUT /api/v1/admin/notes/{id}/audit - 笔记审核
GET /api/v1/admin/users - 用户管理
PUT /api/v1/admin/users/{id}/status - 更新用户状态
```

## 4. 项目结构

### 前端项目结构
```
src/
├── api/                # API请求封装
├── assets/            # 静态资源
├── components/        # 公共组件
├── composables/       # 组合式函数
├── layouts/           # 布局组件
├── router/            # 路由配置
├── stores/            # Pinia状态管理
├── styles/            # 全局样式
├── utils/             # 工具函数
└── views/             # 页面组件
```

### 后端项目结构
```
app/
├── api/                    # API路由层
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── user.py        # 用户相关路由
│   │   ├── note.py        # 笔记相关路由
│   │   └── admin.py       # 管理后台路由
│   └── deps.py            # 依赖注入
│
├── controllers/           # 业务控制层
│   ├── __init__.py
│   ├── user.py           # 用户业务控制
│   ├── note.py           # 笔记业务控制
│   └── admin.py          # 管理业务控制
│
├── core/                 # 核心组件
│   ├── __init__.py
│   ├── config.py         # 配置类
│   ├── security.py       # 安全相关
│   ├── crud.py      # CRUD基类
│   ├── permissions.py    # 权限控制
│   ├── exceptions.py     # 异常处理
│   └── middleware.py     # 中间件
│
├── log/                  # 日志模块
│   ├── __init__.py
│   └── logger.py         # 日志实现
│
├── models/               # 数据模型
│   ├── __init__.py
│   ├── user.py          # 用户模型
│   └── transaction.py    # 交易模型
│
├── schemas/              # 数据校验
│   └── __init__.py      
│
└── utils/               # 工具类
    ├── __init__.py
    ├── jwt.py          # JWT工具
    ├── crypto.py       # 加密工具
    └── helpers.py      # 通用工具
```

## 5. 数据库配置

### Tortoise-ORM 配置
```python
TORTOISE_ORM = {
    "connections": {
        "default": "mysql://user:pass@localhost:3306/dbname"
    },
    "apps": {
        "models": {
            "models": ["app.models.users", "aerich.models"],
            "default_connection": "default",
        },
    },
}

# 数据库初始化
async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.models.users"]}
    )
    await Tortoise.generate_schemas()
```

## 6. 关键功能实现策略

1. 用户认证
- JWT + Redis 实现Token管理
- Tortoise-ORM 实现用户数据操作
- FastAPI 依赖注入实现权限控制

2. 笔记管理
- MongoDB 存储笔记内容
- Redis 缓存热门笔记
- PyMongo 异步操作

3. 支付系统
- 微信/支付宝支付集成
- Redis 实现幂等性控制
- 事务管理确保数据一致性

4. 性能优化
- Redis 缓存热点数据
- MongoDB 索引优化
- Tortoise-ORM 查询优化

## 7. 部署方案

1. 开发环境
- Docker Compose 本地环境
- Vite 开发服务器
- uvicorn 开发服务器

2. 生产环境
- Nginx 反向代理
- Gunicorn + uvicorn
- Docker 容器化部署
- Prometheus + Grafana 监控
