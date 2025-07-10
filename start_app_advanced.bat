@echo off
setlocal enabledelayedexpansion

:: 设置标题和颜色
title 糖尿病智能健康助理系统 - 高级启动脚本
color 0A

echo ======================================================
echo          糖尿病智能健康助理系统 - 启动工具
echo ======================================================
echo.

:: 定义变量
set BACKEND_DIR=backend
set FRONTEND_DIR=frontend
set PYTHON_MIN_VERSION=3.8
set NODE_MIN_VERSION=14.0.0

:: 检查目录是否存在
if not exist %BACKEND_DIR% (
    echo [错误] 未找到后端目录: %BACKEND_DIR%
    echo 请确保脚本放在项目根目录下运行。
    goto :error
)

if not exist %FRONTEND_DIR% (
    echo [错误] 未找到前端目录: %FRONTEND_DIR%
    echo 请确保脚本放在项目根目录下运行。
    goto :error
)

:: 检查Python版本
echo [检查] Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境，请安装Python %PYTHON_MIN_VERSION%或更高版本。
    goto :error
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do (
        set PYTHON_VERSION=%%a
        echo [信息] 检测到Python版本: !PYTHON_VERSION!
    )
)

:: 检查Node.js版本
echo [检查] Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js环境，请安装Node.js %NODE_MIN_VERSION%或更高版本。
    goto :error
) else (
    for /f "tokens=1" %%a in ('node --version') do (
        set NODE_VERSION=%%a
        echo [信息] 检测到Node.js版本: !NODE_VERSION:~1!
    )
)

echo [信息] 环境检查完成。
echo.

:: 询问是否安装依赖
set /p INSTALL_DEPS="是否需要安装/更新依赖? (y/n): "
if /i "%INSTALL_DEPS%"=="y" (
    echo.
    echo [信息] 正在安装后端依赖...
    cd %BACKEND_DIR%
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [警告] 后端依赖安装可能不完整，请检查错误信息。
    ) else (
        echo [成功] 后端依赖安装完成。
    )
    cd ..
    
    echo.
    echo [信息] 正在安装前端依赖...
    cd %FRONTEND_DIR%
    call npm install
    if %errorlevel% neq 0 (
        echo [警告] 前端依赖安装可能不完整，请检查错误信息。
    ) else (
        echo [成功] 前端依赖安装完成。
    )
    cd ..
    echo.
)

:: 询问启动模式
echo 请选择启动模式:
echo [1] 开发模式 - 前后端分离启动(推荐开发使用)
echo [2] 仅启动后端
echo [3] 仅启动前端
echo.
set /p START_MODE="请输入选项(1-3): "

:: 根据选择启动服务
if "%START_MODE%"=="1" (
    echo.
    echo [信息] 正在启动后端服务...
    start "后端服务" cmd /k "cd %BACKEND_DIR% && python main.py"
    
    echo [信息] 等待后端服务启动...
    timeout /t 3 /nobreak > nul
    
    echo [信息] 正在启动前端服务...
    start "前端服务" cmd /k "cd %FRONTEND_DIR% && npm run dev"
    
    echo.
    echo [成功] 服务启动完成！
    echo.
    echo 后端服务运行在: http://localhost:8000
    echo 前端服务运行在: http://localhost:5173
    echo API文档地址: http://localhost:8000/docs
) else if "%START_MODE%"=="2" (
    echo.
    echo [信息] 仅启动后端服务...
    start "后端服务" cmd /k "cd %BACKEND_DIR% && python main.py"
    
    echo.
    echo [成功] 后端服务启动完成！
    echo.
    echo 后端服务运行在: http://localhost:8000
    echo API文档地址: http://localhost:8000/docs
) else if "%START_MODE%"=="3" (
    echo.
    echo [信息] 仅启动前端服务...
    start "前端服务" cmd /k "cd %FRONTEND_DIR% && npm run dev"
    
    echo.
    echo [成功] 前端服务启动完成！
    echo.
    echo 前端服务运行在: http://localhost:5173
) else (
    echo.
    echo [错误] 无效的选项: %START_MODE%
    goto :error
)

echo.
echo [提示] 请不要关闭此窗口，关闭此窗口不会自动停止已启动的服务。
echo [提示] 如需停止服务，请关闭对应的命令行窗口。
echo.

:: 保持窗口打开
pause
goto :eof

:error
echo.
echo [错误] 启动失败，请检查上述错误信息。
pause
exit /b 1 