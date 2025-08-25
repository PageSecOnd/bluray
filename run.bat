@echo off
chcp 65001 >nul
title Blu-ray Menu Player

echo ========================================
echo    Blu-ray Menu Player 蓝光菜单播放器
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python。请先安装 Python 3.7 或更高版本。
    echo.
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Display Python version
echo 检测到 Python:
python --version

:: Check if VLC is installed
echo.
echo 检查 VLC Media Player...
if exist "%ProgramFiles%\VideoLAN\VLC\vlc.exe" (
    echo ✓ 找到 VLC: %ProgramFiles%\VideoLAN\VLC\vlc.exe
) else if exist "%ProgramFiles(x86)%\VideoLAN\VLC\vlc.exe" (
    echo ✓ 找到 VLC: %ProgramFiles(x86)%\VideoLAN\VLC\vlc.exe
) else (
    echo ⚠ 未找到 VLC Media Player
    echo 建议安装 VLC 以获得最佳播放体验
    echo 下载地址: https://www.videolan.org/vlc/
    echo.
)

:: Run the launcher
echo.
echo 启动程序...
python launcher.py

if errorlevel 1 (
    echo.
    echo 程序异常退出。
    pause
)