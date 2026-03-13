#!/bin/bash

# 水质监控系统 - 一键启动脚本

echo ""
echo "========================================"
echo "   水质监控系统 - 一键启动脚本"
echo "========================================"
echo ""

# 检查环境
echo "[1/4] 检查环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端
echo "[2/4] 启动后端服务..."
cd "$(dirname "$0")/src"

if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

echo "📦 激活虚拟环境..."
source venv/bin/activate

echo "📦 安装后端依赖..."
pip install -r requirements.txt > /dev/null 2>&1

echo "📦 执行数据库迁移..."
python manage.py migrate > /dev/null 2>&1

echo "🚀 启动后端服务 (端口8000)..."
gnome-terminal -- bash -c "source venv/bin/activate && python manage.py runserver 8000; exec bash" &
BACKEND_PID=$!

echo ""
echo "[3/4] 启动前端服务..."
cd "$(dirname "$0")/web"

echo "📦 安装前端依赖..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "🚀 启动前端服务 (端口5173)..."
gnome-terminal -- bash -c "npm run dev; exec bash" &
FRONTEND_PID=$!

echo ""
echo "[4/4] 等待服务启动..."
sleep 5

echo ""
echo "========================================"
echo "           🎉 启动完成!"
echo "========================================"
echo ""
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端地址: http://localhost:8000/api"
echo "🔐 登录页面: http://localhost:5173/enhanced-login"
echo ""
echo "👤 测试账号:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "💡 提示: 按 Ctrl+C 停止对应服务"
echo ""

# 打开登录页面
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5173/enhanced-login
elif command -v open > /dev/null; then
    open http://localhost:5173/enhanced-login
fi

echo "按 Ctrl+C 退出脚本..."
trap 'echo ""; echo "正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait
