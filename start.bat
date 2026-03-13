@echo off
title 水质监控系统 - 一键启动
color 0A

echo.
echo ========================================
echo    水质监控系统 - 一键启动脚本
echo ========================================
echo.

echo [1/4] 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到PATH
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装或未添加到PATH
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

echo [2/4] 启动后端服务...
cd /d "%~dp0src"
if not exist "venv" (
    echo 📦 创建Python虚拟环境...
    python -m venv venv
)

echo 📦 激活虚拟环境...
call venv\Scripts\activate.bat

echo 📦 安装后端依赖...
pip install -r requirements.txt >nul 2>&1

echo 📦 执行数据库迁移...
python manage.py migrate >nul 2>&1

echo 🚀 启动后端服务 (端口8000)...
start "Django Backend" cmd /k "call venv\Scripts\activate.bat && python manage.py runserver 8000"

echo.
echo [3/4] 启动前端服务...
cd /d "%~dp0web"

echo 📦 安装前端依赖...
if not exist "node_modules" (
    npm install
)

echo 🚀 启动前端服务 (端口5173)...
start "Vue Frontend" cmd /k "npm run dev"

echo.
echo [4/4] 等待服务启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo           🎉 启动完成!
echo ========================================
echo.
echo 📱 前端地址: http://localhost:5173
echo 🔧 后端地址: http://localhost:8000/api
echo 🔐 登录页面: http://localhost:5173/enhanced-login
echo.
echo 👤 测试账号:
echo    用户名: admin
echo    密码: admin123
echo.
echo 💡 提示: 关闭此窗口不会停止服务
echo    如需停止服务，请手动关闭对应的命令行窗口
echo.

echo 🌐 正在打开登录页面...
start http://localhost:5173/enhanced-login

echo.
echo 按任意键退出...
pause >nul
