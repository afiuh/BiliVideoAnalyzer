@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
setlocal enabledelayedexpansion

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 检测虚拟环境并激活
if exist ".venv\Scripts\python.exe" (
    echo 使用虚拟环境 Python...
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    echo 使用系统 Python...
    set "PYTHON=python"
)

REM 运行主控脚本
echo 开始执行主控脚本 main.py ...
!PYTHON! main.py

echo.
pause