# 河流水质监控系统

> 作者：Yunzenn

基于Django REST Framework + Vue 3的河流水质监控管理系统，使用文件存储替代传统数据库。

## 技术栈

### 后端
- Django 4.2 + Django REST Framework
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
