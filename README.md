# 水质监控系统

一个基于 Vue 3 + Django 的现代化水质监测管理系统，提供实时数据监控、智能分析、异常报警等功能。

## 🌟 项目特色

- **🎯 智能监测**: 实时水质数据采集与监控，支持多监测点管理
- **📊 数据分析**: 丰富的数据可视化图表，支持趋势分析和统计报表
- **⚠️ 异常报警**: 智能异常检测与报警机制，及时通知水质异常
- **🔐 权限管理**: 完善的用户权限体系，支持多角色管理
- **🤖 AI助手**: 集成AI智能分析，提供水质预测和决策建议
- **📱 响应式设计**: 现代化UI界面，支持多设备访问

## 🏗️ 技术栈

### 后端 (Django)
- **框架**: Django 4.2.7 + Django REST Framework
- **数据库**: SQLite 轻量级数据库
- **认证**: JWT Token 认证
- **AI模块**: 支持多模型接入的智能分析
- **数据处理**: Pandas, NumPy, Scikit-learn

### 前端 (Vue 3)
- **框架**: Vue 3 + Composition API
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **构建工具**: Vite
- **图表**: ECharts

## 📁 项目结构

```
homework/
├── src/                    # Django 后端
│   ├── api/                # API 接口
│   │   ├── models.py       # 数据模型
│   │   ├── views.py        # API 视图
│   │   ├── serializers.py  # 序列化器
│   │   └── urls.py        # 路由配置
│   ├── ai_agents/          # AI Agent模块
│   │   ├── core/          # AI核心逻辑
│   │   └── api/           # AI API接口
│   ├── users/              # 用户管理
│   ├── water_quality/      # 项目配置
│   └── manage.py          # Django 管理脚本
├── web/                    # Vue 前端
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── components/    # 公共组件
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   └── utils/         # 工具函数
│   └── package.json
└── README.md
```

## 🚀 启动方式

#### 环境要求
- Python 3.8+
- Node.js 16+

#### 后端启动
```bash
cd src
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

#### 前端启动
```bash
cd web
npm install
npm run dev
```

## 🌐 访问地址

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000/api
- **登录页面**: http://localhost:5173/enhanced-login

## 👤 测试账号

- **用户名**: `admin`
- **密码**: `admin123`

## 📊 核心功能

### 数据管理
- **批量录入**: 支持手动输入、表格批量、文件导入三种方式
- **数据查看**: 多视图展示（表格、时间轴、日历、波形、对比）
- **数据导出**: 支持 CSV 格式导出

### 智能分析
- **趋势分析**: 水质指标变化趋势
- **异常检测**: 基于阈值的智能报警
- **统计报表**: 完整的数据统计分析

### AI 智能助手
- **多模型支持**: 本地LLM、OpenAI、Claude等
- **自然语言查询**: 用自然语言查询水质数据
- **预测分析**: 基于历史数据预测趋势
- **决策建议**: 提供专业的治理建议

## 🔧 开发说明

### API 接口
- **记录管理**: `/api/records/`
- **统计数据**: `/api/records/stats/`
- **报警数据**: `/api/records/alerts/`
- **AI分析**: `/api/ai/`

### 数据模型
- **WaterQualityRecord**: 水质记录核心模型
- **User**: 用户模型（扩展Django用户）

### 权限体系
- **管理员**: 全部权限
- **操作员**: 数据录入和查看
- **观察员**: 仅查看权限

## 📄 许可证

MIT License
