# 河流水质监控管理系统

一个基于Vue 3 + Django + SQLite的现代化水质监控管理平台。

## 🚀 项目特性

- **现代化UI设计** - 采用渐变色彩、卡片布局、动画效果
- **实时数据监控** - 支持水质数据录入、查询、分析
- **智能状态判断** - 自动计算正常/警告/超标状态
- **多维度查询** - 支持时间、地点、指标阈值查询
- **数据可视化** - 集成ECharts图表展示
- **响应式设计** - 适配桌面端和移动端
- **数据导出** - 支持CSV格式数据导出

## 🛠️ 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 现代化构建工具
- **Element Plus** - Vue 3组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **ECharts** - 数据可视化
- **Axios** - HTTP客户端

### 后端
- **Django 4.2** - Python Web框架
- **Django REST Framework** - API开发
- **SQLite** - 轻量级数据库
- **Django CORS** - 跨域支持

## 📁 项目结构

```
homework/
├── src/                    # Django后端
│   ├── api/               # API应用
│   │   ├── models.py      # 数据模型
│   │   ├── views.py       # API视图
│   │   ├── serializers.py # 序列化器
│   │   └── urls.py        # 路由配置
│   └── water_quality/    # 项目配置
│       ├── settings.py    # Django设置
│       └── urls.py        # 主路由
└── web/                     # Vue前端
    ├── src/
    │   ├── views/         # 页面组件
    │   ├── api/           # API调用
    │   ├── layout/        # 布局组件
    │   └── router/        # 路由配置
    ├── package.json          # 依赖配置
    └── vite.config.js        # 构建配置
```

## 🚀 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+
- Git

### 后端启动
```bash
cd src
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_json data/water_quality.json
python manage.py runserver 0.0.0.0:8000
```

### 前端启动
```bash
cd web
npm install
npm run dev
```

### 生产构建
```bash
cd web
npm run build
npm run preview
```

## 📊 核心功能

### 1. 数据管理
- 水质数据录入
- 批量数据导入
- 数据编辑删除
- 数据验证校验

### 2. 高级查询
- 监测点查询
- 时间范围查询
- 指标阈值查询
- 快速查询模板

### 3. 数据分析
- 水质趋势图表
- 统计分析报表
- 异常数据预警
- 数据对比分析

### 4. 系统管理
- 用户权限管理
- 系统配置管理
- 日志监控查看

## 🎨 界面预览

### 高级查询页面
- 🎯 **现代化设计** - 渐变背景、卡片布局
- 📊 **实时统计** - 正常/警告/超标数据统计
- 🔍 **智能查询** - 多条件组合查询
- ⚡ **快速模板** - 预设查询条件
- 📱 **响应式** - 适配各种屏幕尺寸

### 数据分析页面
- 📈 **趋势图表** - 时间序列数据展示
- 📊 **统计报表** - 多维度数据分析
- 🎯 **异常监控** - 实时预警提醒

## 🔧 配置说明

### 数据库配置
```python
# src/water_quality/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### API配置
```python
# 跨域配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### 前端代理
```javascript
// web/vite.config.js
server: {
    proxy: {
        '/api': {
            target: 'http://localhost:8000',
            changeOrigin: true,
        }
    }
}
```

## 📡 API接口

### 水质记录
- `GET /api/records/` - 获取记录列表
- `POST /api/records/` - 创建新记录
- `GET /api/records/{id}/` - 获取单条记录
- `PUT /api/records/{id}/` - 更新记录
- `DELETE /api/records/{id}/` - 删除记录

### 数据统计
- `GET /api/stats/` - 获取统计数据
- `GET /api/analysis/` - 获取分析数据

## 🎯 水质指标标准

| 指标 | 正常范围 | 单位 | 说明 |
|--------|------------|------|------|
| 余氯 | 0.5-4.0 | mg/L | 消毒效果指标 |
| 电导率 | ≤1000 | µS/cm | 水质纯净度 |
| pH值 | 6.5-8.5 | - | 酸碱度指标 |
| ORP | ≥400 | mV | 氧化还原电位 |
| 浊度 | ≤5.0 | NTU | 水质清澈度 |

## 🐛 故障排除

### 常见问题

**Q: 前端构建失败**
```bash
# 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Q: 后端API无响应**
```bash
# 检查Django服务
python manage.py runserver 0.0.0.0:8000

# 检查数据库迁移
python manage.py migrate
```

**Q: 跨域问题**
```python
# 确保settings.py中配置正确
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
```

## 📝 开发指南

### 添加新页面
1. 在 `web/src/views/` 创建组件
2. 在 `web/src/router/index.js` 添加路由
3. 在 `web/src/api/` 添加API调用
4. 更新菜单导航

### 添加新API
1. 在 `src/api/models.py` 定义模型
2. 在 `src/api/serializers.py` 创建序列化器
3. 在 `src/api/views.py` 实现视图
4. 在 `src/api/urls.py` 配置路由
5. 执行数据库迁移

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👥 联系方式

- 项目维护者：水质监控系统团队
- 技术支持：提交Issue或邮件联系

---

**🎉 感谢使用河流水质监控管理系统！**
- 自定义JSON文件存储
- Pydantic数据验证
- CORS跨域支持

### 前端
- Vue 3 + Vite
- Element Plus UI组件库
- Axios HTTP客户端
- 响应式设计

## 功能特性

- ✅ 水质数据增删改查
- ✅ 批量数据上传(CSV)
- ✅ 数据导出功能
- ✅ 实时数据可视化
- ✅ 报警监控与统计
- ✅ 高级查询筛选
- ✅ 主题切换(深色/浅色)

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 8+

### 安装步骤

1. **启动后端**
```bash
cd src
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

2. **启动前端**
```bash
cd web
npm install
npm run dev
```

3. **访问系统**
- 前端：http://localhost:5173
- 后端API：http://localhost:8000/api/

## 项目结构

```
d:\homework\
├── src/                 # 后端(Django)
│   ├── api/            # API应用
│   ├── water_quality/  # 主配置
│   └── data/           # JSON数据存储
├── web/                 # 前端(Vue 3)
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── api/        # API接口
│   │   └── layout/     # 布局组件
│   └── public/         # 静态资源
└── README.md           # 项目说明
```

## API接口

### 水质记录
- `GET /api/records/` - 获取记录列表
- `POST /api/records/` - 创建新记录
- `PUT /api/records/{id}/` - 更新记录
- `DELETE /api/records/{id}/` - 删除记录
- `POST /api/records/batch_delete/` - 批量删除
- `GET /api/records/export/` - 导出数据

### 统计分析
- `GET /api/stats/` - 获取统计数据
- `GET /api/alerts/` - 获取报警信息

## 数据格式

### 水质记录字段
```json
{
  "record_id": 1,
  "point_id": "监测点001",
  "date": "2024-03-11",
  "time": "08:00",
  "chlorine": 2.5,
  "conductivity": 450.0,
  "ph": 7.2,
  "orp": 650.0,
  "turbidity": 1.8
}
```

### 批量上传格式
```csv
监测点ID,日期,时间,余氯(mg/L),电导率(µS/cm),pH值,氧化还原电位(mV),浊度(NTU)
监测点001,2026-03-11,08:00,2.5,450.0,7.2,650.0,1.8
```

## 部署说明

### 开发环境
- 后端：`python manage.py runserver` (8000端口)
- 前端：`npm run dev` (5173端口)

### 生产环境
- 后端：使用Gunicorn + Nginx
- 前端：构建静态文件部署
- 数据存储：JSON文件(需定期备份)

## 注意事项

- 数据存储在JSON文件中，注意备份
- 支持CSV格式批量导入导出
- 前端代理配置指向后端8000端口
- 建议定期清理和备份数据文件

## 许可证

MIT License
