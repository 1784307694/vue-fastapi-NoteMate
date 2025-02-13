# NoteMate - 在线笔记系统

NoteMate是一个基于FastAPI开发的在线笔记系统后端服务，提供了完整的笔记管理、用户认证等功能。

## 技术栈

### 后端框架
- FastAPI: 现代、快速的Web框架
- Tortoise ORM: 异步ORM框架
- MongoDB: 存储笔记内容
- Redis: 缓存和会话管理
- MySQL: 用户数据和系统配置
- Nginx: 反向代理和负载均衡

### 主要功能
- 用户认证和授权
- 笔记的CRUD操作
- 文件上传和管理
- API文档自动生成
- 缓存优化
- 异步处理

## 项目结构
```
NoteMate/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── schemas/           # 数据验证
│   └── utils/             # 工具函数
├── nginx/                 # Nginx配置
│   ├── conf.d/           # Nginx配置文件
│   ├── ssl/              # SSL证书
│   └── logs/             # Nginx日志
├── docker-compose.yml     # Docker编排配置
├── Dockerfile            # 应用容器配置
└── requirements.txt      # Python依赖
```

## 部署指南

### 环境要求
- Docker
- Docker Compose
- Git

### 1. 准备工作
```bash
# 克隆项目
git clone <项目地址>
cd NoteMate

# 创建必要的目录
mkdir -p nginx/conf.d nginx/ssl nginx/logs
mkdir -p app/logs
```

### 2. 配置环境变量
创建或修改 `.env` 文件：
```env
# MySQL配置
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=test
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# MongoDB配置
MONGODB_USER=xiaocaibao
MONGODB_PASSWORD=your_mongodb_password

# Redis配置
REDIS_PASSWORD=your_redis_password
```

### 3. 启动服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看应用日志
docker-compose logs -f app
```

### 4. 访问服务
- API接口: `http://localhost/api/v1/...`
- API文档: `http://localhost/docs`
- 健康检查: `http://localhost/health`

### 5. 维护命令
```bash
# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f [服务名]

# 更新应用
git pull
docker-compose up -d --build app
```

## HTTPS配置（可选）
1. 准备SSL证书
2. 将证书文件放入 `nginx/ssl/` 目录
3. 修改 `nginx/conf.d/default.conf`，取消HTTPS配置的注释
4. 重启Nginx：
```bash
docker-compose restart nginx
```

## 性能优化
1. Nginx配置了以下优化：
   - 静态文件缓存
   - 请求缓冲
   - 超时设置
   - WebSocket支持

2. 应用优化：
   - Redis缓存热点数据
   - 数据库连接池
   - 异步处理

## 安全建议
1. 修改所有默认密码
2. 启用HTTPS
3. 配置防火墙
4. 定期更新依赖
5. 启用日志监控

## 常见问题
1. 服务无法启动
   - 检查端口占用
   - 检查环境变量配置
   - 查看容器日志

2. 数据库连接失败
   - 确认数据库服务状态
   - 检查连接信息
   - 查看数据库日志

3. 性能问题
   - 检查日志中的慢查询
   - 确认缓存是否生效
   - 查看系统资源使用情况

## 备份策略
```bash
# 数据库备份
docker-compose exec mysql mysqldump -u root -p database_name > backup.sql
docker-compose exec mongodb mongodump --uri="mongodb://user:password@localhost:27017" --out=/backup

# Redis备份
docker-compose exec redis redis-cli -a your_redis_password save
```

## 监控建议
1. 使用应用内置的健康检查接口
2. 监控系统资源使用情况
3. 设置日志告警
4. 定期检查备份

## 开发指南
如需进行开发，请参考：
1. API文档：访问 `/docs` 查看完整API文档
2. 项目结构说明
3. 开发环境搭建
4. 测试用例编写

## 贡献指南
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证
[您的许可证类型] 