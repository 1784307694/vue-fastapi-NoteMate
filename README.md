# NoteMate

NoteMate是一个基于 FastAPI + Vue3 + Element Plus 的现代化全栈开发平台，采用前后端分离架构，融合了 RBAC 权限管理、动态路由和 JWT 鉴权等企业级特性。
前端地址：
```
https://github.com/1784307694/NoteMate-admin
https://github.com/1784307694/NoteMate
```

## ✨ 特性

- 🚀 采用 FastAPI + Vue3 + Element Plus 等最新技术栈
- 🔐 细粒度权限控制：实现按钮和接口级别的权限控制，确保不同用户或角色在界面操作和接口访问时具有不同的权限限制。
- 🌐 动态路由：后端动态路由，结合 RBAC（Role-Based Access Control）权限模型，提供精细的菜单路由控制。
- 🔐 JWT鉴权：使用 JSON Web Token（JWT）进行身份验证和授权，增强应用的安全性。
- 💾 多数据源支持 (MySQL + MongoDB + Redis)
- 📦 容器化部署，开箱即用

## 🛠 技术栈

### 后端技术
- **FastAPI**: 高性能异步 Web 框架
- **Tortoise ORM**: 高效的异步 ORM 框架
- **MongoDB**: 文档存储引擎，处理笔记内容
- **Redis**: 分布式缓存和会话管理
- **MySQL**: 关系型数据存储
- **Nginx**: 反向代理和负载均衡

### 前端技术
- **Vue3**: 渐进式 JavaScript 框架
- **Element Plus**: 优雅的 UI 组件库
- **Vite**: 下一代前端构建工具
- **TypeScript**: 类型安全的 JavaScript 超集
- **Pinia**: 直观的状态管理

## 🏗 系统架构

```
NoteMate/
├── 后端服务 (Backend)
│   ├── app/                    # 应用核心
│   │   ├── api/               # RESTful API
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # 数据验证
│   │   └── utils/             # 工具集
│   └── tests/                 # 单元测试
├── 基础设施 (Infrastructure)
│   ├── nginx/                 # 反向代理
│   │   ├── conf.d/           # Nginx配置
│   │   ├── ssl/              # SSL证书
│   │   └── logs/             # 访问日志
│   └── docker/               # 容器编排
└── 部署配置
    ├── docker-compose.yml    # 服务编排
    ├── Dockerfile           # 容器构建
    └── requirements.txt     # 依赖管理
```

## 🚀 快速开始

### 环境要求
- Docker Engine (20.10.0+)
- Docker Compose (2.0.0+)
- Git

### 1. 部署准备
```bash
# 创建服务目录
mkdir -p nginx/{conf.d,ssl,logs}
mkdir -p app/logs
```

### 2. 环境配置
创建 `.env` 配置文件：
```env
# 数据库配置
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_DATABASE=notemate
MYSQL_USER=notemate
MYSQL_PASSWORD=your_secure_password

# MongoDB配置
MONGODB_USER=notemate
MONGODB_PASSWORD=your_secure_password

# Redis配置
REDIS_PASSWORD=your_secure_password
```

### 3. 服务启动
```bash
# 构建并启动服务集群
docker-compose up -d

# 查看服务状态
docker-compose ps

# 监控应用日志
docker-compose logs -f app
```

### 4. 访问服务
- RESTful API: `http://localhost/api/v1/`
- API文档: `http://localhost/docs`

### 5. 运维指令
```bash
# 服务重启
docker-compose restart

# 优雅停止
docker-compose down

# 日志查看
docker-compose logs -f [service_name]
```

## 🔒 安全加固

### HTTPS 配置
1. 配置 SSL 证书
2. 证书部署至 `nginx/ssl/`
3. 启用 HTTPS 配置
4. 重载 Nginx：
```bash
docker-compose restart nginx
```

### 安全最佳实践
1. 实施强密码策略
2. 启用 HTTPS 加密传输
3. 配置防火墙规则
4. 日志审计

## ⚡ 性能优化

### Nginx 优化
- 静态资源缓存
- 请求缓冲控制
- 连接超时优化
- WebSocket 支持

### 应用优化
- Redis 多级缓存
- 数据库连接池
- 异步任务处理


## 💾 数据备份
```bash
# MySQL备份
docker-compose exec mysql mysqldump -u root -p notemate > backup.sql

# MongoDB备份
docker-compose exec mongodb mongodump --uri="mongodb://user:password@localhost:27017" --out=/backup

# Redis持久化
docker-compose exec redis redis-cli -a your_redis_password save
```

## 🔥 即将推出
- [ ] 实时协作编辑
- [ ] AI 辅助写作
- [ ] 知识图谱
- [ ] 多语言支持

