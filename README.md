# 河流水质监控管理系统

一个基于Django REST Framework + Vue 3 + Element Plus的现代化水质监控管理平台，使用文件存储替代传统数据库，轻量级且易于部署。

## 🌟 系统特点

- 🚀 **高性能**：基于成熟框架，响应迅速
- 💾 **轻量级**：使用文件存储，无需数据库配置
- 📊 **可视化**：丰富的图表展示，直观易懂
- 🌙 **主题切换**：支持深色/浅色主题
- 📱 **响应式**：适配多种设备屏幕
- ⚡ **易部署**：一键启动，最小化配置

## 🛠️ 技术栈

### 后端
- **Django 4.2** - Web框架
- **Django REST Framework** - API框架
- **自定义文件存储** - 替代数据库
- **Pydantic** - 数据验证

### 前端
- **Vue 3** - 前端框架
- **Element Plus** - UI组件库
- **ECharts** - 数据可视化
- **Vite** - 构建工具
- **Pinia** - 状态管理

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 8+ 或 yarn 1.22+

### 📋 启动步骤

#### 第一步：后端启动
```bash
# 1. 进入后端目录
cd src

# 2. 创建Python虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. 安装Python依赖
pip install -r requirements.txt

# 5. 启动后端服务
python manage.py runserver
```

#### 第二步：前端启动
```bash
# 1. 打开新终端，进入前端目录
cd web

# 2. 安装Node.js依赖
npm install
# 或者使用 yarn
yarn install

# 3. 启动前端开发服务器
npm run dev
# 或者使用 yarn
yarn dev
```

#### 第三步：访问系统
启动成功后，在浏览器中访问：
- 🌐 **前端界面**: http://localhost:5173
- 🔌 **后端API**: http://localhost:8000/api/
- ⚙️ **管理后台**: http://localhost:8000/admin/

### 🎯 快速验证
1. 访问 http://localhost:5173 查看系统界面
2. 点击"数据管理"查看示例数据
3. 尝试新增一条水质记录
4. 查看"仪表盘"的数据可视化
5. 检查"报警监控"是否有超标数据

### ⚠️ 常见问题

**Q: 提示"Couldn't import Django"**
A: 确保已激活虚拟环境并安装依赖

**Q: 前端启动失败**
A: 检查Node.js版本是否为16+

**Q: 无法访问API**
A: 确保后端服务在8000端口正常运行

## 📁 项目结构

```
water-quality-monitoring-system/
├── src/                            # 后端项目 (原water_quality_backend)
│   ├── water_quality/              # Django主配置
│   ├── api/                        # API应用
│   │   ├── views.py               # 视图层
│   │   ├── serializers.py         # 序列化器
│   │   ├── models.py              # 数据模型
│   │   ├── file_storage.py        # 文件存储服务
│   │   └── utils.py               # 工具函数
│   ├── data/                      # 数据存储
│   └── requirements.txt           # Python依赖
├── web/                           # 前端项目 (原water_quality_frontend)
│   ├── src/
│   │   ├── views/                 # 页面组件
│   │   │   ├── Dashboard.vue      # 仪表盘
│   │   │   ├── Records.vue        # 数据管理
│   │   │   ├── Query.vue          # 高级查询
│   │   │   └── Alerts.vue         # 报警监控
│   │   ├── components/            # 通用组件
│   │   │   └── charts/            # 图表组件
│   │   ├── api/                   # API接口
│   │   ├── stores/                # 状态管理
│   │   └── utils/                 # 工具函数
│   └── package.json               # Node.js依赖
├── design_document.md              # 设计文档
├── deployment.md                   # 部署文档
├── user_manual.md                 # 用户手册
└── README.md                      # 项目说明
```

## � 功能模块

### 🎯 仪表盘
- **KPI指标**：总记录数、平均pH值、平均浊度、报警数量
- **趋势图表**：7天水质变化趋势，支持多指标切换
- **实时仪表盘**：5个指标的实时数值显示
- **报警预览**：最新5条报警记录

### � 数据管理
- **数据表格**：支持排序、筛选、分页
- **CRUD操作**：新增、编辑、删除记录
- **批量操作**：批量删除、数据导出
- **实时验证**：表单数据实时验证

### � 高级查询
- **动态条件**：可视化构建查询条件
- **多条件组合**：支持AND逻辑组合
- **操作符丰富**：等于、大于、小于、介于等
- **结果导出**：查询结果JSON导出

### 🚨 报警监控
- **统计卡片**：总报警数、警告级别、严重级别
- **报警分析**：类型分布饼图、趋势折线图
- **报警列表**：分级显示、详情查看
- **阈值标准**：查看各项指标正常范围

## 📈 监测指标

| 指标名称 | 单位 | 正常范围 | 说明 |
|----------|------|----------|------|
| 余氯 | mg/L | 0.5 - 4.0 | 消毒剂残留量 |
| 电导率 | µS/cm | ≤ 1000 | 水中导电能力 |
| pH值 | - | 6.5 - 8.5 | 酸碱度 |
| 氧化还原电位 | mV | ≥ 400 | 氧化还原能力 |
| 浊度 | NTU | ≤ 5.0 | 水体浑浊程度 |

## 🔧 API接口

### 基础CRUD
- `GET /api/records/` - 获取记录列表
- `POST /api/records/` - 创建新记录
- `GET /api/records/{id}/` - 获取单条记录
- `PUT /api/records/{id}/` - 更新记录
- `DELETE /api/records/{id}/` - 删除记录

### 高级功能
- `POST /api/records/query/` - 高级查询
- `GET /api/records/alerts/` - 获取报警记录
- `GET /api/records/stats/` - 获取统计数据
- `GET /api/records/dashboard_data/` - 仪表盘数据
- `POST /api/records/batch_delete/` - 批量删除

## 🎨 界面预览

### 仪表盘
- 专业的数据可视化界面
- KPI指标卡片带动画效果
- 多种图表类型展示
- 实时报警信息推送

### 数据管理
- 现代化表格设计
- 行内编辑功能
- 批量操作支持
- 智能数据验证

### 报警监控
- 直观的报警统计
- 多维度报警分析
- 详细的报警信息
- 趋势预测功能

## 🌙 主题系统

系统支持深色和浅色两种主题：
- **浅色主题**：清新明亮，适合日间使用
- **深色主题**：护眼模式，适合夜间使用
- **自动切换**：一键切换，实时生效
- **状态保存**：记住用户偏好设置

## 📱 响应式设计

- **桌面端**：完整功能体验
- **平板端**：适配触控操作
- **手机端**：核心功能可用
- **自适应布局**：根据屏幕尺寸自动调整

## 🔒 安全特性

- **输入验证**：前后端双重验证
- **数据校验**：严格的类型和范围检查
- **文件安全**：防止路径遍历攻击
- **接口保护**：CORS配置和请求限制

## 🚀 部署方案

### 开发环境
```bash
# 后端
python manage.py runserver

# 前端
npm run dev
```

### 生产环境
```bash
# 使用Gunicorn + Nginx
gunicorn --workers 3 --bind unix:/app/water_quality.sock water_quality.wsgi:application
nginx -c /etc/nginx/nginx.conf
```

### Docker部署
```bash
# 使用Docker Compose
docker-compose up -d
```

## 📚 文档

- 📋 [设计文档](./design_document.md) - 系统设计和技术架构
- 🚀 [部署文档](./deployment.md) - 环境配置和部署指南
- 📖 [用户手册](./user_manual.md) - 功能使用和操作指南

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Django](https://www.djangoproject.com/) - 强大的Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - 优秀的Vue组件库
- [ECharts](https://echarts.apache.org/) - 强大的数据可视化库

## 📞 联系我们

如果您有任何问题或建议，请联系：
- 📧 邮箱：support@waterquality.com
- 🌐 官网：https://waterquality.com
- 💬 微信群：扫码加入技术交流群

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

## 2. 系统架构

### 2.1 整体架构图
```
┌─────────────────┐    HTTP请求    ┌─────────────────┐
│   前端 (Vue 3)   │ ←──────────→   │ 后端 (Django)   │
│                 │                │                 │
│ - Element Plus  │                │ - REST API      │
│ - ECharts       │                │ - 文件存储服务   │
│ - 响应式设计     │                │ - 数据验证       │
└─────────────────┘                └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │   数据存储       │
                                    │                 │
                                    │ - JSON文件      │
                                    │ - 自动备份       │
                                    │ - 数据迁移       │
                                    └─────────────────┘
```

### 2.2 模块结构

#### 2.2.1 后端模块
```
water_quality_backend/
├── water_quality/          # 主项目配置
│   ├── settings.py         # 系统配置
│   ├── urls.py            # 路由配置
│   └── wsgi.py            # WSGI配置
├── api/                    # API应用
│   ├── views.py           # 视图层
│   ├── serializers.py     # 序列化器
│   ├── models.py          # 数据模型
│   ├── file_storage.py    # 文件存储服务
│   ├── filters.py         # 过滤器
│   └── utils.py           # 工具函数
├── data/                   # 数据目录
│   └── water_quality.json  # 数据文件
└── manage.py              # Django管理脚本
```

#### 2.2.2 前端模块
```
water_quality_frontend/
├── src/
│   ├── views/             # 页面组件
│   │   ├── Dashboard.vue  # 仪表盘
│   │   ├── Records.vue    # 数据管理
│   │   ├── Query.vue      # 高级查询
│   │   └── Alerts.vue     # 报警监控
│   ├── components/        # 通用组件
│   │   └── charts/        # 图表组件
│   ├── api/              # API接口
│   ├── stores/           # 状态管理
│   ├── utils/            # 工具函数
│   └── assets/           # 静态资源
├── public/               # 公共资源
└── index.html           # 入口文件
```

## 3. 数据结构设计

### 3.1 水质记录数据结构
```json
{
  "record_id": 1,
  "point_id": "监测点001",
  "date": "2026-03-11",
  "time": "08:00",
  "chlorine": 2.5,
  "conductivity": 450.0,
  "ph": 7.2,
  "orp": 650.0,
  "turbidity": 1.8,
  "create_time": "2026-03-11T08:00:00"
}
```

### 3.2 字段说明
| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| record_id | Integer | 记录ID（自动生成） | 1 |
| point_id | String | 监测点标识 | "监测点001" |
| date | String | 日期（YYYY-MM-DD） | "2024-03-11" |
| time | String | 时间（HH:MM） | "08:00" |
| chlorine | Float | 余氯值（mg/L） | 2.5 |
| conductivity | Float | 电导率（µS/cm） | 450.0 |
| ph | Float | pH值 | 7.2 |
| orp | Float | 氧化还原电位（mV） | 650.0 |
| turbidity | Float | 浊度（NTU） | 1.8 |
| create_time | String | 创建时间（ISO格式） | "2024-03-11T08:00:00" |

### 3.3 报警阈值配置
```python
ALERT_THRESHOLDS = {
    'chlorine': {'min': 0.5, 'max': 4.0},      # mg/L
    'conductivity': {'max': 1000},             # µS/cm
    'ph': {'min': 6.5, 'max': 8.5},            # pH值
    'orp': {'min': 400},                       # mV
    'turbidity': {'max': 5.0}                  # NTU
}
```

## 4. API接口设计

### 4.1 基础CRUD接口

#### 4.1.1 获取记录列表
```
GET /api/records/
参数：
- page: 页码（默认1）
- page_size: 每页数量（默认20）
- search: 搜索关键词
- ordering: 排序字段

响应：
{
  "count": 100,
  "next": "http://localhost:8000/api/records/?page=2",
  "previous": null,
  "results": [...]
}
```

#### 4.1.2 获取单条记录
```
GET /api/records/{id}/
响应：单条记录对象
```

#### 4.1.3 创建记录
```
POST /api/records/
请求体：记录数据（不包含record_id）
响应：创建的记录对象
```

#### 4.1.4 更新记录
```
PUT /api/records/{id}/
请求体：完整记录数据
响应：更新后的记录对象
```

#### 4.1.5 删除记录
```
DELETE /api/records/{id}/
响应：204 No Content
```

### 4.2 高级功能接口

#### 4.2.1 高级查询
```
POST /api/records/query/
请求体：
{
  "point_id": "监测点001",
  "date_start": "2024-03-01",
  "date_end": "2024-03-31",
  "ph_min": 6.5,
  "ph_max": 8.5,
  "sort_by": "date",
  "sort_desc": true
}
响应：查询结果列表
```

#### 4.2.2 报警记录
```
GET /api/records/alerts/
参数：
- limit: 返回数量限制（默认50）
响应：报警记录列表
```

#### 4.2.3 统计数据
```
GET /api/records/stats/
响应：
{
  "total_records": 100,
  "avg_values": {...},
  "max_values": {...},
  "min_values": {...},
  "alert_count": 15
}
```

#### 4.2.4 仪表盘数据
```
GET /api/records/dashboard_data/
响应：
{
  "stats": {...},
  "trend_data": [...],
  "recent_alerts": [...],
  "current_record": {...}
}
```

#### 4.2.5 批量删除
```
POST /api/records/batch_delete/
请求体：
{
  "record_ids": [1, 2, 3]
}
响应：
{
  "message": "成功删除 3 条记录",
  "deleted_count": 3,
  "total_requested": 3
}
```

## 5. 核心算法设计

### 5.1 文件存储服务算法

#### 5.1.1 数据读取算法
```python
def read_all():
    """读取所有记录"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
```

#### 5.1.2 查询过滤算法
```python
def query(filters):
    """复杂查询算法"""
    data = read_all()
    result = []
    
    for item in data:
        match = True
        
        # 监测点过滤
        if 'point_id' in filters:
            if filters['point_id'] not in item.get('point_id', ''):
                match = False
        
        # 日期范围过滤
        if 'date_start' in filters and 'date_end' in filters:
            item_date = item.get('date', '')
            if not (filters['date_start'] <= item_date <= filters['date_end']):
                match = False
        
        # 数值范围过滤
        for field in ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']:
            if f'{field}_min' in filters:
                if item.get(field, 0) < filters[f'{field}_min']:
                    match = False
            if f'{field}_max' in filters:
                if item.get(field, 0) > filters[f'{field}_max']:
                    match = False
        
        if match:
            result.append(item)
    
    # 排序
    if 'sort_by' in filters:
        reverse = filters.get('sort_desc', False)
        result.sort(key=lambda x: x.get(filters['sort_by'], ''), reverse=reverse)
    
    return result
```

### 5.2 报警检测算法

#### 5.2.1 超标检测
```python
def get_alerts(thresholds):
    """获取超标报警记录"""
    data = read_all()
    alerts = []
    
    for item in data:
        alert_items = []
        alert_level = '一般'
        
        # 检查各项指标
        for field, threshold in thresholds.items():
            value = item.get(field)
            if value is None:
                continue
            
            if 'min' in threshold and value < threshold['min']:
                alert_items.append(f"{field}偏低")
                alert_level = '严重'
            elif 'max' in threshold and value > threshold['max']:
                alert_items.append(f"{field}偏高")
                alert_level = '严重' if value > threshold['max'] * 1.5 else '警告'
        
        if alert_items:
            alert_record = item.copy()
            alert_record['alert_items'] = alert_items
            alert_record['alert_level'] = alert_level
            alerts.append(alert_record)
    
    return sorted(alerts, key=lambda x: x.get('date', ''), reverse=True)
```

### 5.3 数据统计算法

#### 5.3.1 统计计算
```python
def get_statistics():
    """获取统计数据"""
    data = read_all()
    
    if not data:
        return {
            'total_records': 0,
            'avg_values': {},
            'max_values': {},
            'min_values': {},
            'alert_count': 0
        }
    
    numeric_fields = ['chlorine', 'conductivity', 'ph', 'orp', 'turbidity']
    stats = {
        'total_records': len(data),
        'avg_values': {},
        'max_values': {},
        'min_values': {},
        'alert_count': 0
    }
    
    # 计算各字段的统计值
    for field in numeric_fields:
        values = [item.get(field, 0) for item in data if item.get(field) is not None]
        if values:
            stats['avg_values'][field] = round(sum(values) / len(values), 2)
            stats['max_values'][field] = max(values)
            stats['min_values'][field] = min(values)
    
    # 计算报警数量
    stats['alert_count'] = len(get_alerts(thresholds))
    
    return stats
```

## 6. 前端组件设计

### 6.1 页面组件

#### 6.1.1 仪表盘（Dashboard.vue）
- **功能**：系统概览、KPI展示、趋势图表、报警预览
- **组件**：KPI卡片、折线图、仪表盘图、饼图、报警列表
- **数据流**：调用dashboard_data接口获取综合数据

#### 6.1.2 数据管理（Records.vue）
- **功能**：数据CRUD操作、批量操作、数据导出
- **组件**：数据表格、分页器、表单对话框
- **数据流**：标准REST API调用

#### 6.1.3 高级查询（Query.vue）
- **功能**：动态查询条件、结果展示、数据导出
- **组件**：查询条件构建器、结果表格、详情对话框
- **数据流**：调用query接口执行复杂查询

#### 6.1.4 报警监控（Alerts.vue）
- **功能**：报警统计、报警列表、报警详情、趋势分析
- **组件**：统计卡片、图表组件、报警列表、详情对话框
- **数据流**：调用alerts和stats接口

### 6.2 图表组件

#### 6.2.1 折线图（LineChart.vue）
- **用途**：展示数据趋势
- **特性**：多指标、平滑曲线、响应式、主题适配

#### 6.2.2 饼图（PieChart.vue）
- **用途**：展示数据分布
- **特性**：环形设计、动画效果、图例显示

#### 6.2.3 仪表盘图（GaugeChart.vue）
- **用途**：展示实时指标
- **特性**：多仪表盘、颜色分区、数值显示

#### 6.2.4 柱状图（BarChart.vue）
- **用途**：展示数据对比
- **特性**：渐变色彩、数值标签、交互效果

### 6.3 状态管理

#### 6.3.1 应用状态（app.js）
```javascript
export const useAppStore = defineStore('app', () => {
  const theme = ref('light')           // 主题模式
  const sidebarCollapsed = ref(false)  // 侧边栏状态
  const breadcrumb = ref([])           // 面包屑导航
  
  const setTheme = (newTheme) => {...}
  const toggleSidebar = () => {...}
  const setBreadcrumb = (items) => {...}
  
  return {
    theme, sidebarCollapsed, breadcrumb,
    setTheme, toggleSidebar, setBreadcrumb
  }
})
```

## 7. 性能优化策略

### 7.1 前端优化
- **代码分割**：路由级别懒加载
- **组件缓存**：keep-alive缓存页面组件
- **图片优化**：图标使用SVG，减少HTTP请求
- **打包优化**：Vite构建优化，去除无用代码

### 7.2 后端优化
- **文件缓存**：内存缓存热点数据
- **分页查询**：避免一次性加载大量数据
- **索引优化**：JSON文件按日期分组存储
- **异步处理**：耗时操作异步执行

### 7.3 数据存储优化
- **文件分片**：按月分片存储，提高查询效率
- **数据压缩**：JSON文件压缩存储
- **备份策略**：定期自动备份
- **清理机制**：自动清理过期数据

## 8. 安全考虑

### 8.1 输入验证
- **前端验证**：表单字段实时验证
- **后端验证**：序列化器严格验证
- **类型检查**：Pydantic模型验证
- **范围检查**：数值范围限制

### 8.2 文件安全
- **路径验证**：防止路径遍历攻击
- **权限控制**：文件读写权限限制
- **备份加密**：敏感数据加密存储
- **日志记录**：操作日志完整记录

### 8.3 接口安全
- **CORS配置**：跨域请求控制
- **请求限制**：API调用频率限制
- **错误处理**：敏感信息隐藏
- **HTTPS支持**：传输加密

## 9. 扩展性设计

### 9.1 水平扩展
- **负载均衡**：多实例部署
- **数据分片**：按监测点分片存储
- **缓存集群**：Redis集群支持
- **微服务**：模块化服务拆分

### 9.2 功能扩展
- **实时推送**：WebSocket支持
- **移动端**：响应式设计适配
- **报表系统**：PDF报表生成
- **权限管理**：用户角色权限

### 9.3 数据扩展
- **数据库迁移**：支持PostgreSQL迁移
- **数据导入**：Excel批量导入
- **API集成**：第三方数据源
- **数据同步**：多端数据同步

## 10. 测试策略

### 10.1 单元测试
- **后端测试**：文件存储服务测试
- **前端测试**：组件单元测试
- **工具测试**：工具函数测试
- **API测试**：接口功能测试

### 10.2 集成测试
- **端到端测试**：完整业务流程
- **性能测试**：并发访问测试
- **兼容性测试**：浏览器兼容性
- **响应式测试**：多设备适配

### 10.3 用户测试
- **可用性测试**：用户体验评估
- **压力测试**：系统负载测试
- **安全测试**：安全漏洞扫描
- **回归测试**：版本更新验证

---

## 总结

本设计文档详细描述了河流水质监控管理系统的技术架构、数据结构、API设计、核心算法和性能优化等关键方面。系统采用成熟的技术栈，具有良好的可扩展性和维护性，能够满足水质监控的实际需求。

通过模块化设计和标准化接口，系统支持功能扩展和技术升级，为后续的系统演进奠定了坚实基础。
