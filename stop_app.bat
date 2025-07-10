@echo off
echo 正在停止糖尿病智能健康助理系统服务...
echo.

:: 设置标题和颜色
title 糖尿病智能健康助理系统 - 停止服务
color 0C

:: 停止后端服务 (Python进程)
echo [信息] 正在停止后端服务...
taskkill /f /im python.exe /fi "WINDOWTITLE eq 后端服务*" >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] 后端服务已停止。
) else (
    echo [信息] 未发现运行中的后端服务。
)

:: 停止前端服务 (Node进程)
echo [信息] 正在停止前端服务...
taskkill /f /im node.exe /fi "WINDOWTITLE eq 前端服务*" >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] 前端服务已停止。
) else (
    echo [信息] 未发现运行中的前端服务。
)

:: 停止可能的npm进程
echo [信息] 正在停止npm进程...
taskkill /f /im npm.cmd >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] npm进程已停止。
) else (
    echo [信息] 未发现运行中的npm进程。
)

echo.
echo [完成] 所有服务已停止。
echo.
pause 