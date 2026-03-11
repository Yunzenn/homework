# 河流水质监控管理系统 - 部署文档

## 1. 环境要求

### 1.1 系统要求
- **操作系统**：Linux (Ubuntu 20.04+ / CentOS 7+) / Windows 10+ / macOS 10.15+
- **内存**：最低 2GB，推荐 4GB+
- **存储**：最低 10GB 可用空间
- **网络**：稳定的互联网连接

### 1.2 软件依赖

#### 后端环境
- **Python**：3.8+ (推荐 3.11)
- **pip**：最新版本
- **virtualenv**：Python虚拟环境工具

#### 前端环境
- **Node.js**：16.0+ (推荐 18.0+)
- **npm**：8.0+ 或 **yarn**：1.22+

#### 生产环境（可选）
- **Nginx**：1.18+ (反向代理)
- **Gunicorn**：20.1+ (WSGI服务器)
- **Supervisor**：4.2+ (进程管理)

## 2. 开发环境搭建

### 2.1 克隆项目
```bash
git clone <repository-url>
cd water-quality-monitoring-system
```

### 2.2 后端环境配置

#### 2.2.1 创建虚拟环境
```bash
cd src

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2.2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.2.3 初始化数据
```bash
# 创建数据目录
mkdir -p data

# 初始化Django
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser
```

#### 2.2.4 启动后端服务
```bash
python manage.py runserver
```
服务将在 `http://localhost:8000` 启动

### 2.3 前端环境配置

#### 2.3.1 安装依赖
```bash
cd web
npm install
# 或使用 yarn
yarn install
```

#### 2.3.2 启动前端服务
```bash
npm run dev
# 或使用 yarn
yarn dev
```
服务将在 `http://localhost:5173` 启动

### 2.4 访问系统
- 前端界面：http://localhost:5173
- 后端API：http://localhost:8000/api/
- 管理后台：http://localhost:8000/admin/

## 3. 生产环境部署

### 3.1 服务器准备

#### 3.1.1 系统更新
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 3.1.2 安装必要软件
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum install -y python3 python3-pip nginx
```

#### 3.1.3 安装Node.js
```bash
# 使用NodeSource仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 3.2 后端部署

#### 3.2.1 部署应用代码
```bash
# 创建项目目录
sudo mkdir -p /var/www/water_quality
sudo chown $USER:$USER /var/www/water_quality

# 复制代码
cp -r src /var/www/water_quality/backend
cd /var/www/water_quality/backend
```

#### 3.2.2 配置Python环境
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn
```

#### 3.2.3 配置Django设置
```bash
# 编辑 settings.py
sudo nano water_quality/settings.py
```

修改以下配置：
```python
# 生产环境配置
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'server-ip']

# 静态文件配置
STATIC_ROOT = '/var/www/water_quality/static/'
MEDIA_ROOT = '/var/www/water_quality/media/'

# 数据目录
DATA_DIR = '/var/www/water_quality/data/'
```

#### 3.2.4 收集静态文件
```bash
python manage.py collectstatic --noinput
```

#### 3.2.5 创建数据目录
```bash
mkdir -p /var/www/water_quality/data
mkdir -p /var/www/water_quality/static
mkdir -p /var/www/water_quality/media
```

#### 3.2.6 配置Gunicorn
创建Gunicorn配置文件：
```bash
sudo nano /etc/systemd/system/water_quality.service
```

```ini
[Unit]
Description=Water Quality Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/water_quality/backend
Environment="PATH=/var/www/water_quality/backend/venv/bin"
ExecStart=/var/www/water_quality/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/water_quality/water_quality.sock \
          water_quality.wsgi:application

[Install]
WantedBy=multi-user.target
```

启动Gunicorn服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start water_quality
sudo systemctl enable water_quality
```

### 3.3 前端部署

#### 3.3.1 构建前端应用
```bash
cd /var/www/water_quality/frontend
npm install
npm run build
```

#### 3.3.2 配置Nginx
创建Nginx配置文件：
```bash
sudo nano /etc/nginx/sites-available/water_quality
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/water_quality/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://unix:/var/www/water_quality/water_quality.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 管理后台
    location /admin/ {
        proxy_pass http://unix:/var/www/water_quality/water_quality.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static/ {
        alias /var/www/water_quality/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 媒体文件
    location /media/ {
        alias /var/www/water_quality/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/water_quality /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3.4 SSL证书配置（可选）

#### 3.4.1 使用Let's Encrypt
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 4. Docker部署（可选）

### 4.1 Dockerfile配置

#### 4.1.1 后端Dockerfile
```dockerfile
# src/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "water_quality.wsgi:application"]
```

#### 4.1.2 前端Dockerfile
```dockerfile
# web/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4.2 Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./src
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,127.0.0.1

  frontend:
    build: ./web
    ports:
      - "80:80"
    depends_on:
      - backend
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 4.3 启动Docker服务
```bash
docker-compose up -d
```

## 5. 环境变量配置

### 5.1 后端环境变量
创建 `.env` 文件：
```bash
# Django配置
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# 数据库配置（如果使用）
DATABASE_URL=sqlite:///db.sqlite3

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/water_quality.log
```

### 5.2 前端环境变量
创建 `.env.production` 文件：
```bash
VITE_API_BASE_URL=https://your-domain.com/api
VITE_APP_TITLE=河流水质监控管理系统
```

## 6. 监控和日志

### 6.1 日志配置

#### 6.1.1 Django日志设置
在 `settings.py` 中添加：
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/water_quality/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

#### 6.1.2 创建日志目录
```bash
sudo mkdir -p /var/log/water_quality
sudo chown www-data:www-data /var/log/water_quality
```

### 6.2 系统监控

#### 6.2.1 进程监控
```bash
# 检查Gunicorn状态
sudo systemctl status water_quality

# 检查Nginx状态
sudo systemctl status nginx

# 查看日志
sudo journalctl -u water_quality -f
sudo tail -f /var/log/nginx/error.log
```

#### 6.2.2 性能监控
安装监控工具：
```bash
# 安装htop
sudo apt install htop

# 安装iotop
sudo apt install iotop

# 监控系统资源
htop
iotop
```

## 7. 备份策略

### 7.1 数据备份

#### 7.1.1 自动备份脚本
创建备份脚本：
```bash
sudo nano /usr/local/bin/backup_water_quality.sh
```

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/water_quality"
DATE=$(date +%Y%m%d_%H%M%S)
DATA_DIR="/var/www/water_quality/data"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据文件
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" -C "$DATA_DIR" .

# 备份数据库（如果使用）
# pg_dump water_quality > "$BACKUP_DIR/db_$DATE.sql"

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/data_$DATE.tar.gz"
```

#### 7.1.2 设置定时备份
```bash
sudo chmod +x /usr/local/bin/backup_water_quality.sh
sudo crontab -e
# 添加以下行（每天凌晨2点备份）：
# 0 2 * * * /usr/local/bin/backup_water_quality.sh
```

### 7.2 应用备份

#### 7.2.1 代码备份
```bash
# 备份应用代码
tar -czf /var/backups/water_quality/app_$DATE.tar.gz /var/www/water_quality
```

#### 7.2.2 配置备份
```bash
# 备份配置文件
sudo cp /etc/nginx/sites-available/water_quality /var/backups/water_quality/nginx_$DATE.conf
sudo cp /etc/systemd/system/water_quality.service /var/backups/water_quality/service_$DATE.service
```

## 8. 故障排除

### 8.1 常见问题

#### 8.1.1 后端启动失败
```bash
# 检查Python环境
source venv/bin/activate
python --version

# 检查依赖
pip list

# 检查Django设置
python manage.py check

# 查看详细错误
python manage.py runserver --verbosity=2
```

#### 8.1.2 前端构建失败
```bash
# 清理缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install

# 检查Node.js版本
node --version
npm --version
```

#### 8.1.3 Nginx配置错误
```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log

# 重新加载配置
sudo nginx -s reload
```

#### 8.1.4 权限问题
```bash
# 修复文件权限
sudo chown -R www-data:www-data /var/www/water_quality
sudo chmod -R 755 /var/www/water_quality

# 修复数据目录权限
sudo chmod -R 777 /var/www/water_quality/data
```

### 8.2 性能问题

#### 8.2.1 响应慢
```bash
# 检查系统资源
free -h
df -h
top

# 优化Gunicorn配置
# 增加worker数量
# 调整超时设置
```

#### 8.2.2 内存不足
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 重启服务释放内存
sudo systemctl restart water_quality
sudo systemctl restart nginx
```

## 9. 安全加固

### 9.1 防火墙配置
```bash
# 安装ufw
sudo apt install ufw

# 配置防火墙
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# 启用防火墙
sudo ufw enable
```

### 9.2 系统更新
```bash
# 设置自动安全更新
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 9.3 访问控制
```bash
# 限制SSH访问
sudo nano /etc/ssh/sshd_config
# 添加：
# PermitRootLogin no
# PasswordAuthentication no
# AllowUsers your_username

sudo systemctl restart ssh
```

## 10. 维护指南

### 10.1 定期维护任务

#### 10.1.1 每日任务
- 检查系统状态
- 查看错误日志
- 监控磁盘空间
- 验证服务运行

#### 10.1.2 每周任务
- 系统更新检查
- 备份验证
- 性能监控
- 安全扫描

#### 10.1.3 每月任务
- 依赖包更新
- 配置优化
- 容量规划
- 文档更新

### 10.2 更新流程

#### 10.2.1 应用更新
```bash
# 备份当前版本
sudo cp -r /var/www/water_quality /var/backups/water_quality/backup_$(date +%Y%m%d)

# 更新代码
cd /var/www/water_quality/backend
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重新构建前端
cd ../frontend
npm install
npm run build

# 重启服务
sudo systemctl restart water_quality
sudo systemctl restart nginx
```

#### 10.2.2 回滚操作
```bash
# 恢复备份
sudo systemctl stop water_quality nginx
sudo rm -rf /var/www/water_quality
sudo cp -r /var/backups/water_quality/backup_20240311 /var/www/water_quality
sudo systemctl start water_quality nginx
```

---

## 总结

本部署文档提供了从开发环境到生产环境的完整部署指南，包括环境配置、服务部署、监控维护等关键环节。按照本文档操作，可以快速搭建稳定可靠的水质监控系统。

定期维护和监控是保证系统稳定运行的关键，建议建立完善的运维流程和监控机制。
