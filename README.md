# 水质监控系统

一个基于 Vue 3 + Django 的现代化水质监测管理系统，提供实时数据监控、智能分析、异常报警等功能。系统采用前后端分离架构，支持多用户权限管理，适用于水务公司、环保部门等水质监测场景。

## 🌟 项目特色

- **🎯 智能监测**: 实时水质数据采集与监控，支持多监测点管理
- **📊 数据分析**: 丰富的数据可视化图表，支持趋势分析和统计报表
- **⚠️ 异常报警**: 智能异常检测与报警机制，及时通知水质异常
- **🔐 权限管理**: 完善的用户权限体系，支持多角色管理
- **🤖 AI助手**: 集成AI智能分析，提供水质预测和决策建议
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
- **AI Agent**: 智能分析模块，支持多模型接入
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
│   ├── ai_agents/          # AI Agent模块
│   │   ├── api/            # AI API接口
│   │   ├── core/           # AI核心逻辑
│   │   │   ├── model_interface.py      # 模型接口
│   │   │   ├── enhanced_agent.py      # 增强Agent
│   │   │   └── enhanced_data_query_agent.py # 数据查询Agent
│   │   ├── config.py       # AI配置管理
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
│   │   │   ├── ai.js      # AI接口
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
│   │       ├── AIChat.vue        # AI智能助手
│   │       ├── Alerts.vue        # 报警管理
│   │       ├── DataAnalysis.vue  # 数据分析
│   │       ├── Records.vue      # 数据管理
│   │       ├── BatchInput.vue   # 数据录入
│   │       └── login/          # 登录页面
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
├── start_ai_service.py      # AI服务启动脚本
└── README.md
```

## 🤖 AI智能助手

### 功能特色
- **多模型支持**: 本地LLM、OpenAI、Claude、自定义API
- **智能配置**: 可视化配置界面，一键切换模型
- **实时测试**: 配置后立即测试连接状态
- **数据查询**: 自然语言查询水质数据
- **趋势分析**: 智能分析数据变化趋势
- **异常检测**: 自动识别水质异常情况
- **预测分析**: 基于历史数据预测未来趋势
- **决策建议**: 提供专业的治理建议

### 快速配置
1. 访问AI智能助手：http://localhost:5173/ai-chat
2. 点击右上角⚙️设置按钮
3. 选择模型类型并填写配置
4. 点击"测试连接"验证配置
5. 保存配置开始使用

### 支持的模型
- **本地模型**: Ollama、LM Studio等
  ```bash
  # 启动本地服务
  python start_ai_service.py --service ollama
  ```
- **OpenAI**: GPT-3.5、GPT-4系列
  - API密钥：sk-...
  - 模型选择：gpt-3.5-turbo、gpt-4
- **Claude**: Claude 3 Sonnet、Haiku、Opus
  - API密钥：sk-ant-...
  - 模型选择：claude-3-sonnet-20240229
- **自定义API**: 任何OpenAI兼容的API服务

### 使用示例
```javascript
// 数据查询
"P-042今天pH值多少？"
"最近一周的浊度数据"
"pH值大于8.5的记录"

// 趋势分析
"最近一周pH值变化趋势"
"溶解氧含量分析"

// 异常诊断
"为什么余氯突然升高？"
"pH值异常的原因"

// 预测分析
"明天水质会超标吗？"
"未来一周pH值预测"
```

### 配置参数
- **温度参数**: 0.0-1.0，控制生成随机性
- **最大Token**: 1000-4000，限制回复长度
- **连接超时**: 30秒，API请求超时时间
