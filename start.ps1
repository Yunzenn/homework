# 水质监控系统 - 一键启动脚本 (PowerShell)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   水质监控系统 - 一键启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查环境
Write-Host "[1/4] 检查环境..." -ForegroundColor Yellow
try {
    python --version | Out-Null
    $pythonOk = $true
} catch {
    Write-Host "❌ Python 未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}

try {
    node --version | Out-Null
    $nodeOk = $true
} catch {
    Write-Host "❌ Node.js 未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 环境检查通过" -ForegroundColor Green
Write-Host ""

# 启动后端
Write-Host "[2/4] 启动后端服务..." -ForegroundColor Yellow
Set-Location $PSScriptRoot\src

if (-not (Test-Path "venv")) {
    Write-Host "📦 创建Python虚拟环境..." -ForegroundColor Blue
    python -m venv venv
}

Write-Host "📦 激活虚拟环境..." -ForegroundColor Blue
& venv\Scripts\Activate.ps1

Write-Host "📦 安装后端依赖..." -ForegroundColor Blue
pip install -r requirements.txt | Out-Null

Write-Host "📦 执行数据库迁移..." -ForegroundColor Blue
python manage.py migrate | Out-Null

Write-Host "🚀 启动后端服务 (端口8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& venv\Scripts\Activate.ps1; python manage.py runserver 8000" -WindowStyle Normal

Write-Host ""
Write-Host "[3/4] 启动前端服务..." -ForegroundColor Yellow
Set-Location $PSScriptRoot\web

Write-Host "📦 安装前端依赖..." -ForegroundColor Blue
if (-not (Test-Path "node_modules")) {
    npm install
}

Write-Host "🚀 启动前端服务 (端口5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "[4/4] 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           🎉 启动完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 前端地址: http://localhost:5173" -ForegroundColor White
Write-Host "🔧 后端地址: http://localhost:8000/api" -ForegroundColor White
Write-Host "🔐 登录页面: http://localhost:5173/enhanced-login" -ForegroundColor White
Write-Host ""
Write-Host "👤 测试账号:" -ForegroundColor White
Write-Host "   用户名: admin" -ForegroundColor Gray
Write-Host "   密码: admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 提示: 关闭此窗口不会停止服务" -ForegroundColor Yellow
Write-Host "    如需停止服务，请手动关闭对应的PowerShell窗口" -ForegroundColor Yellow
Write-Host ""

# 打开登录页面
Start-Process "http://localhost:5173/enhanced-login"

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
