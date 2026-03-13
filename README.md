# 水质监控系统

一个基于 Vue 3 + Django 的现代化水质监测管理系统，提供实时数据监控、智能分析、异常报警等功能。系统采用前后端分离架构，支持多用户权限管理，适用于水务公司、环保部门等水质监测场景。

## 🌟 项目特色

- **🎯 智能监测**: 实时水质数据采集与监控，支持多监测点管理
- **📊 数据分析**: 丰富的数据可视化图表，支持趋势分析和统计报表
- **⚠️ 异常报警**: 智能异常检测与报警机制，及时通知水质异常
- **🔐 权限管理**: 完善的用户权限体系，支持多角色管理
- **🤖 AI助手**: 集成AI智能分析，提供水质预测和决策建议 (开发中)
- **📱 响应式设计**: 现代化UI界面，支持多设备访问

## 🏢 应用场景

- **🏭 水务公司**: 日常水质监测管理，确保供水安全
- **🌍 环保部门**: 环境水质监控，污染源追踪
- **💧 自来水厂**: 源水到出厂全流程水质监控
- **🏗️ 工业园区**: 工业废水排放监测与管理
- **🏞️ 景区管理**: 景观水体质量维护
- **🔬 科研机构**: 水质数据收集与研究分析

## 🏗️ 技术架构

### 后端架构 (Django)
- **RESTful API**: 标准化接口设计，支持前后端分离
- **JWT认证**: 无状态认证机制，安全可靠
- **权限控制**: 基于角色的权限管理 (RBAC)
- **数据库**: SQLite轻量级数据库，易于部署
- **异步处理**: 支持AI Agent异步任务处理

### 前端架构 (Vue 3)
- **组件化开发**: 可复用的Vue组件设计
- **状态管理**: Pinia集中状态管理
- **路由管理**: Vue Router单页应用路由
- **UI框架**: Element Plus现代化组件库
- **构建工具**: Vite快速构建和热更新

### 数据流程
```
水质传感器 → 数据采集 → 后端API → 数据处理 → 前端展示
                    ↓
                AI分析 → 智能预测 → 决策建议
```

## 🚀 启动方式

### 🎯 一键启动 (推荐)
```bash
# Windows
start.bat

# 或使用PowerShell
start.ps1

# Linux/macOS
chmod +x start.sh
./start.sh
```

### 🔧 手动启动

### 环境要求
- Python 3.8+
- Node.js 16+

### 后端启动
```bash
cd src
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### 前端启动
```bash
cd web
npm install
npm run dev
```

### 访问地址
- 前端：http://localhost:5173
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
│   │   ├── models.py       # 数据模型
│   │   ├── views.py        # API 视图
│   │   └── urls.py         # 路由配置
│   ├── ai_agents/          # AI Agent模块 (待开发)
│   │   ├── api/            # AI API接口
│   │   ├── core/           # AI核心逻辑
│   │   └── urls.py         # AI路由配置
│   ├── users/              # 用户管理
│   │   ├── models.py       # 用户模型
│   │   ├── views.py        # 用户视图
│   │   └── serializers.py   # 序列化器
│   ├── water_quality/      # 项目配置
│   │   ├── settings.py     # Django 设置
│   │   └── urls.py         # 主路由
│   └── manage.py           # Django 管理脚本
├── web/                    # Vue 前端
│   ├── src/
│   │   ├── api/           # API 调用
│   │   │   ├── auth.js    # 认证接口
│   │   │   ├── ai.js      # AI接口 (待开发)
│   │   │   └── waterQuality.js # 业务接口
│   │   ├── components/    # 公共组件
│   │   ├── layout/        # 布局组件
│   │   │   └── index.vue  # 主布局
│   │   ├── router/        # 路由配置
│   │   │   └── index.js  # 路由定义
│   │   ├── stores/        # 状态管理
│   │   │   └── auth.js    # 认证状态
│   │   ├── utils/         # 工具函数
│   │   │   └── request.js # HTTP 请求
│   │   └── views/         # 页面组件
│   │       ├── Dashboard.vue      # 主界面
│   │       ├── Records.vue        # 数据管理
│   │       ├── BatchInput.vue     # 数据录入
│   │       ├── DataAnalysis.vue   # 数据分析
│   │       ├── Alerts.vue         # 报警监控
│   │       ├── AIChat.vue         # AI智能助手 (待开发)
│   │       └── login/             # 登录页面
│   │           ├── EnhancedAnimatedLogin.vue
│   │           ├── ForgotPassword.vue
│   │           ├── Register.vue
│   │           └── ResetPassword.vue
│   ├── package.json
│   └── vite.config.js
├── test_login.html          # 开发测试页面
├── start.bat               # Windows 启动脚本
├── start.ps1               # PowerShell 启动脚本
├── start.sh                # Linux/macOS 启动脚本
└── README.md
```
