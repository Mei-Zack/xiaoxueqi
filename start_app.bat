@echo off
echo 正在启动糖尿病智能健康助理系统...
echo.

:: 设置标题
title 糖尿病智能健康助理系统

:: 设置颜色
color 0A

echo [信息] 检查环境...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境，请安装Python 3.8或更高版本。
    goto :error
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js环境，请安装Node.js 14或更高版本。
    goto :error
)

echo [信息] 环境检查完成，开始启动服务...
echo.

:: 创建两个新的命令行窗口分别运行后端和前端
echo [信息] 正在启动后端服务...
start "后端服务" cmd /k "cd backend && python main.py"

:: 等待2秒确保后端已启动
timeout /t 2 /nobreak > nul

echo [信息] 正在启动前端服务...
start "前端服务" cmd /k "cd frontend && npm run dev"

echo.
echo [成功] 服务启动完成！
echo.
echo 后端服务运行在: http://localhost:8000
echo 前端服务运行在: http://localhost:5173
echo.
echo 请不要关闭此窗口，关闭此窗口将导致服务停止。
echo 如需停止服务，请按Ctrl+C或直接关闭所有相关窗口。
echo.

:: 保持窗口打开
pause
goto :eof

:error
echo.
echo [错误] 启动失败，请检查上述错误信息。
pause 