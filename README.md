# 水质监控系统 - 详细文档

一个基于 Vue 3 + Django 的水质监测管理系统，提供数据录入、可视化分析、异常报警和 AI 智能问答。

## 技术栈

### 后端（Django）
- Django 4.2.7 + Django REST Framework
- SQLite
- JWT 认证
- `ai_agents` 多模型 AI 模块（本地/OpenAI/Claude/自定义）

### 前端（Vue 3）
- Vue 3 + Vite + Pinia + Vue Router
- Element Plus + ECharts

### 流式 AI（Vercel AI SDK）
- 根目录 Serverless Function：`api/vercel-ai/chat.js`
- 前端入口：`web/src/api/ai.js -> streamChat()`
- 聊天页：`web/src/views/AIChat.vue`

## 详细项目结构

```text
homework/
├── api/                                     # Vercel Functions（根目录部署）
│   └── vercel-ai/
│       └── chat.js                          # AI SDK 流式桥接到 Django /api/ai/chat/
├── src/                                     # Django 后端
│   ├── api/                                 # 业务 API 模块
│   │   ├── __init__.py
│   │   ├── admin.py                         # Django Admin 配置
│   │   ├── apps.py                          # 应用配置
│   │   ├── models.py                        # 数据模型
│   │   ├── serializers.py                   # API 序列化器
│   │   ├── urls.py                          # URL 路由
│   │   └── views.py                         # API 视图
│   ├── ai_agents/                           # AI Agent 模块
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── api/                             # AI API 接口
│   │   │   ├── __init__.py
│   │   │   ├── urls.py                      # AI API 路由配置
│   │   │   └── views.py                     # AI API 视图（主要入口）
│   │   ├── config.py                        # AI 模型配置管理
│   │   ├── core/                            # AI 核心逻辑
│   │   │   ├── __init__.py
│   │   │   ├── agent_manager.py             # AI Agent 管理器
│   │   │   ├── db_tools.py                  # 数据库查询工具
│   │   │   ├── model_interface.py           # 模型接口抽象层
│   │   │   └── smart_chat_agent.py          # 智能对话 Agent（核心）
│   │   └── urls.py                          # AI 模块路由
│   ├── users/                               # 用户与权限模块
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                        # 用户模型
│   │   ├── serializers.py                   # 用户序列化器
│   │   ├── urls.py                          # 用户路由
│   │   └── views.py                         # 用户视图（登录/注册）
│   ├── water_quality/                       # Django 项目配置
│   │   ├── __init__.py
│   │   ├── asgi.py                          # ASGI 配置
│   │   ├── settings.py                      # 项目设置
│   │   ├── urls.py                          # 主路由配置
│   │   └── wsgi.py                          # WSGI 配置
│   ├── logs/                                # 日志目录
│   │   └── django.log                       # Django 日志文件
│   ├── manage.py                            # Django 管理脚本
│   └── requirements.txt                     # Python 依赖
├── web/                                     # Vue 前端
│   ├── public/                              # 静态资源
│   ├── src/
│   │   ├── api/                             # API 接口封装
│   │   │   ├── ai.js                        # AI 相关 API
│   │   │   ├── auth.js                      # 认证 API
│   │   │   └── index.js                     # API 统一导出
│   │   ├── assets/                          # 资源文件
│   │   ├── components/                      # 公共组件
│   │   ├── router/                          # 路由配置
│   │   │   └── index.js
│   │   ├── stores/                          # Pinia 状态管理
│   │   │   ├── auth.js                      # 认证状态
│   │   │   └── index.js
│   │   ├── utils/                           # 工具函数
│   │   │   └── request.js                   # HTTP 请求封装
│   │   ├── views/                           # 页面组件
│   │   │   ├── AIChat.vue                   # AI 聊天页面
│   │   │   ├── Dashboard.vue                # 仪表板
│   │   │   ├── Login.vue                    # 登录页面
│   │   │   └── Register.vue                 # 注册页面
│   │   ├── App.vue                          # 根组件
│   │   └── main.js                          # 应用入口
│   ├── vite.config.js                       # Vite 配置
│   └── package.json                         # Node.js 依赖
└── README.md                                # 项目说明
```

## 核心模块详细说明

### 1. AI Agents 模块 (`src/ai_agents/`)

#### 1.1 API 接口层 (`api/views.py`)

**主要函数：**
- `ai_chat(request)` - AI 聊天主接口
  - 功能：处理前端 AI 聊天请求
  - 输入：用户消息、上下文、AI 配置
  - 输出：AI 响应结果
  - 特性：支持多种 AI 模型（本地 Ollama、OpenAI、Claude）

#### 1.2 核心智能体 (`core/smart_chat_agent.py`)

**主要类：`SmartChatAgent`**

**核心方法：**
- `process_query(message, context)` - 主处理入口
  - 功能：处理用户查询的完整流程
  - 步骤：意图分析 → 条件提取 → 数据查询 → AI 生成

- `_analyze_intent(message)` - 意图识别
  - 功能：分析用户查询意图
  - 支持意图：`data_query`、`analysis`、`health_check`、`maintenance`、`comparison`、`equipment_query`、`alert_query`、`statistics`、`monitoring_point`、`trend`、`general`
  - 返回：意图类型、置信度、匹配信息

- `_extract_query_conditions(message)` - 查询条件提取
  - 功能：从消息中提取结构化查询条件
  - 提取内容：监测点ID、地理位置、时间范围、水质指标、限制条数

- `_extract_point_ids(message)` - 监测点ID提取
  - 支持格式：`P-042`、`监测点001`、`A1-01`、`SITE_002`等
  - 特性：动态正则匹配，无需硬编码

- `_extract_indicators(message)` - 水质指标提取
  - 支持指标：pH、余氯、电导率、浊度、氨氮、溶解氧、总磷、总氮、COD、BOD等
  - 特性：中英文对照映射

- `_extract_date_range(message)` - 时间范围提取
  - 支持表达：`今天`、`昨天`、`上周`、`最近7天`、`2023/10/01`等
  - 特性：多种日期格式和相对时间

**处理方法：**
- `_handle_data_query()` - 数据查询处理
- `_handle_maintenance_query()` - 运维查询处理
- `_handle_comparison_query()` - 对比查询处理
- `_handle_health_check_query()` - 健康度查询处理
- `_handle_general_chat()` - 通用对话处理

#### 1.3 模型接口 (`core/model_interface.py`)

**主要类：**
- `BaseModelInterface` - 模型接口抽象基类
- `LocalLLMModel` - 本地 Ollama 模型实现
- `OpenAIModel` - OpenAI API 模型实现
- `ClaudeModel` - Claude API 模型实现

**核心方法：**
- `generate_text(prompt, options)` - 文本生成
  - 功能：调用 AI 模型生成文本
  - 参数：提示词、生成选项（温度、最大token等）
  - 返回：生成的文本内容

#### 1.4 数据库工具 (`core/db_tools.py`)

**主要类：`DatabaseQueryTools`**

**核心方法：**
- `get_water_quality_data()` - 水质数据查询
  - 功能：根据条件查询水质监测数据
  - 参数：监测点ID、时间范围、指标类型、限制条数
  - 返回：格式化的水质数据列表

- `format_water_quality_data()` - 数据格式化
  - 功能：将数据库数据格式化为易读格式
  - 特性：添加单位、异常标记、状态指示

### 2. 用户认证模块 (`src/users/`)

#### 2.1 视图层 (`views.py`)

**主要视图：**
- `LoginView` - 用户登录
  - 功能：处理用户登录请求
  - 输入：用户名、密码、记住登录
  - 输出：JWT token、用户信息
  - 特性：登录日志记录

- `RegisterView` - 用户注册
  - 功能：处理用户注册请求
  - 输入：用户名、邮箱、密码
  - 输出：注册结果、用户信息

#### 2.2 模型层 (`models.py`)

**主要模型：**
- `User` - 用户模型
  - 字段：用户名、邮箱、密码哈希、创建时间
  - 特性：Django 抽象用户基类扩展

### 3. 前端 Vue 模块 (`web/src/`)

#### 3.1 API 封装 (`api/`)

**ai.js - AI 接口：**
- `chat(data)` - AI 聊天接口
- `query(data)` - 数据查询接口
- `analysis(data)` - 数据分析接口
- `streamChat(data, handlers)` - 流式聊天接口
- `getAIConfig()` - 获取 AI 配置

**auth.js - 认证接口：**
- `login(data)` - 用户登录
- `register(data)` - 用户注册
- `logout()` - 用户登出
- `refreshToken()` - 刷新 token
- `getUserInfo()` - 获取用户信息

#### 3.2 页面组件 (`views/`)

**AIChat.vue - AI 聊天页面：**
- 功能：AI 智能对话界面
- 特性：实时对话、历史记录、流式输出、错误处理
- 主要方法：
  - `sendMessage()` - 发送消息
  - `handleStreamResponse()` - 处理流式响应
  - `loadHistory()` - 加载历史记录

**Dashboard.vue - 仪表板：**
- 功能：数据可视化展示
- 特性：图表展示、实时数据、异常报警

#### 3.3 状态管理 (`stores/`)

**auth.js - 认证状态：**
- 状态：用户信息、登录状态、token
- 方法：`login()`、`logout()`、`refreshToken()`

#### 3.4 工具函数 (`utils/`)

**request.js - HTTP 请求：**
- 功能：axios 实例封装
- 特性：请求/响应拦截器、token 自动添加、错误处理
- 配置：60秒超时、自动重试、loading 状态

## 本地启动

### 环境要求
- Python 3.10+
- Node.js 18+
- 本地 Ollama（可选，用于本地 AI 模型）

### 1) 启动后端（8000）

```bash
cd src
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2) 启动前端（5173）

```bash
cd web
npm install
npm run dev
```

### 3) 启动本地 Ollama（可选）

```bash
# 安装 Ollama
# 下载模型
ollama pull qwen2.5-coder:7b
# 启动服务
ollama serve
```

## 本地访问

- 前端：`http://localhost:5173`
- 后端 API：`http://localhost:8000/api`
- AI 聊天 API：`http://localhost:8000/api/ai/chat/`
- 用户登录：`http://localhost:8000/api/auth/login/`

## AI 模块特性

### 意图识别能力
- **数据查询**：`"杭州水质怎么样"`、`"找一下pH数据"`
- **健康度评估**：`"水质稳吗"`、`"有没有好转"`
- **运维查询**：`"传感器什么时候清洗"`、`"设备离线了吗"`
- **数据对比**：`"对比一下上周和上个月的数据"`
- **设备查询**：`"监测点状态"`、`"设备维护记录"`

### 实体提取能力
- **监测点ID**：`P-042`、`A1-01`、`SITE_002`、`监测点001`
- **时间表达**：`今天`、`上周`、`2023/10/01`、`最近7天`
- **水质指标**：pH、余氯、氨氮、溶解氧、总磷、总氮、COD、BOD
- **地理位置**：杭州、西湖、钱塘江等

### 日志追踪
- **完整链路**：从请求接收到响应返回的每个环节
- **性能监控**：模型输入输出、响应时间、错误追踪
- **调试支持**：详细的匹配日志和异常堆栈

## 部署说明

### Vercel 部署（根目录部署）
- Project Root：仓库根目录（`homework`）
- 环境变量：`DJANGO_API_BASE_URL=https://<your-django-domain>`
- 前端请求路径：`/api/vercel-ai/chat`

### Docker 部署
```dockerfile
# 后端 Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 常用接口

### 数据接口
- `GET /api/records/` - 获取水质记录
- `POST /api/records/` - 创建水质记录
- `GET /api/records/stats/` - 获取统计数据
- `GET /api/records/alerts/` - 获取报警信息

### 用户接口
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/logout/` - 用户登出
- `GET /api/auth/user/` - 获取用户信息

### AI 接口
- `POST /api/ai/chat/` - AI 聊天
- `POST /api/ai/query/` - 数据查询
- `POST /api/ai/analysis/` - 数据分析
- `POST /api/ai/test-ollama/` - 测试 Ollama 连接

## 开发指南

### 添加新的 AI 模型
1. 在 `core/model_interface.py` 中继承 `BaseModelInterface`
2. 实现必要的抽象方法
3. 在 `api/views.py` 中添加模型配置

### 扩展意图识别
1. 在 `smart_chat_agent.py` 的 `intent_patterns` 中添加新模式
2. 在 `process_query` 中添加对应的处理方法
3. 实现具体的业务逻辑

### 添加新的水质指标
1. 在 `_extract_indicators` 中添加指标映射
2. 在数据库模型中添加对应字段
3. 更新数据格式化逻辑

## 许可证

MIT License
