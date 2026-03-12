# 水质监控系统

一个基于 Vue 3 + Django 的水质监测管理系统，提供实时数据监控、分析和报警功能。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Django 4.2+
- Vue 3+

### 安装步骤

#### 1. 后端启动
```bash
cd src
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### 2. 前端启动
```bash
cd web
npm install
npm run dev
```

#### 3. 访问系统
- 前端地址：http://localhost:5173
- 后端API：http://localhost:8000/api
- 登录页面：http://localhost:5173/enhanced-login

### 测试账号
- 用户名：`admin`
- 密码：`admin123`

## 📁 项目结构

```
homework/
├── src/                    # Django 后端
│   ├── api/                # API 接口
│   ├── users/              # 用户管理
│   ├── water_quality/      # 项目配置
│   └── manage.py           # Django 管理脚本
├── web/                    # Vue 前端
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── components/    # 公共组件
│   │   ├── layout/        # 布局组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面组件
│   └── package.json
└── README.md
```

## 🎯 核心功能

### 主要页面
- **主界面** (`/dashboard`) - 数据概览和KPI展示
- **数据查看** (`/records`) - 水质数据列表和操作
- **数据录入** (`/batch-input`) - 批量数据导入
- **高级查询** (`/query`) - 数据筛选和搜索
- **数据分析** (`/analysis`) - 数据可视化分析
- **报警监控** (`/alerts`) - 异常报警管理

### 用户功能
- ✅ 用户登录/登出
- ✅ JWT 认证授权
- ✅ 页面权限控制
- ✅ 用户状态保持

## 🛠 技术栈

### 后端技术
- **Django 4.2** - Web 框架
- **Django REST Framework** - API 开发
- **SimpleJWT** - JWT 认证
- **SQLite** - 数据库

### 前端技术
- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端

## 📊 API 接口

### 认证接口
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `GET /api/auth/profile/` - 用户信息

### 数据接口
- `GET /api/records/` - 获取记录列表
- `POST /api/records/` - 创建新记录
- `PUT /api/records/{id}/` - 更新记录
- `DELETE /api/records/{id}/` - 删除记录

## 🔧 开发指南

### 添加新页面
1. 在 `web/src/views/` 创建组件
2. 在 `web/src/router/index.js` 添加路由
3. 在侧边栏菜单添加导航

### 添加新接口
1. 在 `src/api/` 添加 URL 配置
2. 在 `src/users/views.py` 添加视图
3. 在 `web/src/api/` 添加前端调用

## 🐛 常见问题

### 401 认证错误
确保前端请求头使用 `Bearer` 格式：
```javascript
Authorization: Bearer <token>
```

### 页面无法访问
检查路由配置和认证状态，确保已正确登录。

### 数据加载失败
检查后端服务是否正常运行，API 接口是否正确配置。

## 📝 更新日志

### v1.0.0 (2024-03-12)
- ✅ 完成基础功能开发
- ✅ 实现用户认证系统
- ✅ 添加数据管理功能
- ✅ 完善页面导航和权限控制

## 📄 许可证

MIT License
