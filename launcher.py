#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher script for Blu-ray Menu Player
This script checks dependencies and launches the main application.
"""

import sys
import platform
import subprocess

def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 7):
        print("错误: 需要 Python 3.7 或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_windows():
    """Check if running on Windows"""
    if platform.system() != "Windows":
        print("警告: 此程序主要为 Windows 系统设计")
        print(f"当前系统: {platform.system()}")
        response = input("是否继续运行? (y/n): ")
        return response.lower() in ['y', 'yes', '是']
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    # Check tkinter
    try:
        import tkinter
        print("✓ tkinter 已安装")
    except ImportError:
        missing_deps.append("tkinter (Python GUI 库)")
        
    # Check VLC
    try:
        import vlc
        print("✓ python-vlc 已安装")
    except ImportError:
        missing_deps.append("python-vlc")
        
    # Check Pillow
    try:
        from PIL import Image
        print("✓ Pillow 已安装")
    except ImportError:
        missing_deps.append("Pillow")
        
    return missing_deps

def install_dependencies(missing_deps):
    """Try to install missing dependencies"""
    print(f"\n发现缺失的依赖: {', '.join(missing_deps)}")
    
    # Filter out tkinter as it can't be installed via pip
    pip_deps = [dep for dep in missing_deps if not dep.startswith("tkinter")]
    
    if "tkinter (Python GUI 库)" in missing_deps:
        print("\n警告: tkinter 缺失。")
        print("解决方案:")
        print("- 在 Ubuntu/Debian: sudo apt-get install python3-tk")
        print("- 在 Windows: 重新安装 Python 并确保选择 'tcl/tk and IDLE' 选项")
        
    if pip_deps:
        print(f"\n尝试安装 pip 依赖: {', '.join(pip_deps)}")
        response = input("是否自动安装? (y/n): ")
        
        if response.lower() in ['y', 'yes', '是']:
            try:
                # Map dependency names to pip package names
                pip_names = []
                for dep in pip_deps:
                    if dep == "python-vlc":
                        pip_names.append("python-vlc")
                    elif dep == "Pillow":
                        pip_names.append("Pillow")
                        
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + pip_names)
                print("✓ 依赖安装完成")
                return True
            except subprocess.CalledProcessError:
                print("✗ 依赖安装失败")
                return False
                
    return len(missing_deps) == 0

def main():
    """Main launcher function"""
    print("=== Blu-ray Menu Player 启动器 ===\n")
    
    # Check Python version
    if not check_python_version():
        input("按回车键退出...")
        sys.exit(1)
        
    # Check operating system
    if not check_windows():
        sys.exit(1)
        
    # Check dependencies
    print("\n检查依赖...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        if not install_dependencies(missing_deps):
            print("\n无法安装所有依赖。请手动安装后重试。")
            print("\n安装命令:")
            print("pip install -r requirements.txt")
            input("按回车键退出...")
            sys.exit(1)
            
        # Re-check after installation
        missing_deps = check_dependencies()
        if missing_deps:
            print(f"\n仍有依赖缺失: {', '.join(missing_deps)}")
            input("按回车键退出...")
            sys.exit(1)
    
    print("\n✓ 所有依赖检查通过")
    print("\n启动 Blu-ray Menu Player...")
    
    try:
        # Import and run the main application
        from bluray_player import main as run_player
        run_player()
    except Exception as e:
        print(f"\n启动失败: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()