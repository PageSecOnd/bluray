#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for BD-J (Blu-ray Disc Java) support functionality
This script demonstrates the new BD-J menu capabilities.
"""

import tempfile
import shutil
from pathlib import Path
import struct

from bluray_player import BlurayParser, BlurayBDJParser, BlurayMenuNavigator


def create_mock_bdj_disc(base_path):
    """Create a mock Blu-ray disc with BD-J support for demonstration"""
    bdmv_path = Path(base_path) / "BDMV"
    
    # Create basic BDMV structure
    (bdmv_path / "PLAYLIST").mkdir(parents=True)
    (bdmv_path / "STREAM").mkdir()
    (bdmv_path / "CLIPINF").mkdir()
    (bdmv_path / "JAR").mkdir()
    (bdmv_path / "BDJO").mkdir()
    
    # Create mock playlist files
    playlist_data = b"MPLS" + b"\x00" * 996  # 1KB playlist
    (bdmv_path / "PLAYLIST" / "00000.mpls").write_bytes(playlist_data)
    
    large_playlist_data = b"MPLS" + b"\x00" * 9996  # 10KB playlist
    (bdmv_path / "PLAYLIST" / "00001.mpls").write_bytes(large_playlist_data)
    
    # Create mock video files
    (bdmv_path / "STREAM" / "00000.m2ts").write_bytes(b"M2TS" + b"\x00" * 100000)  # ~100KB
    (bdmv_path / "STREAM" / "00001.m2ts").write_bytes(b"M2TS" + b"\x00" * 50000)   # ~50KB
    
    # Create mock BD-J files
    # JAR file (simulated)
    jar_content = b"PK" + b"JAR_CONTENT" * 1000  # Mock JAR file
    (bdmv_path / "JAR" / "00000.jar").write_bytes(jar_content)
    (bdmv_path / "JAR" / "12345.jar").write_bytes(jar_content + b"_INTERACTIVE")
    
    # BDJO files with structured data
    bdjo_data_main = struct.pack('>HH', 0x1000, 0x0001) + b"MAIN_MENU_APP" + b"\x00" * 200
    (bdmv_path / "BDJO" / "00000.bdjo").write_bytes(bdjo_data_main)
    
    bdjo_data_interactive = struct.pack('>HH', 0x2000, 0x0002) + b"INTERACTIVE_FEATURES" + b"\x00" * 300
    (bdmv_path / "BDJO" / "12345.bdjo").write_bytes(bdjo_data_interactive)
    
    return str(bdmv_path)


def demo_bdj_detection():
    """Demonstrate BD-J detection capabilities"""
    print("=" * 60)
    print("BD-J 检测演示")
    print("=" * 60)
    
    # Create temporary test disc
    test_dir = tempfile.mkdtemp()
    try:
        bdmv_path = create_mock_bdj_disc(test_dir)
        
        # Test BD-J parser
        bdj_parser = BlurayBDJParser(bdmv_path)
        
        print(f"BDMV 路径: {bdmv_path}")
        print(f"BD-J 支持: {'✅ 是' if bdj_parser.has_bdj_support() else '❌ 否'}")
        
        if bdj_parser.has_bdj_support():
            applications = bdj_parser.get_bdj_applications()
            print(f"发现 {len(applications)} 个 BD-J 应用:")
            
            for i, app in enumerate(applications, 1):
                print(f"\n应用 {i}:")
                print(f"  名称: {app['bdjo_name']}")
                print(f"  优先级: {app['priority']}")
                print(f"  JAR 文件数量: {len(app['jar_files'])}")
                print(f"  菜单项数量: {len(app['menu_items'])}")
                
                # Show menu items
                print("  菜单项:")
                for item in app['menu_items']:
                    print(f"    - {item['title']} ({item['action']})")
    
    finally:
        shutil.rmtree(test_dir)


def demo_bdj_parser_integration():
    """Demonstrate BD-J integration with main parser"""
    print("\n" + "=" * 60)
    print("BD-J 解析器集成演示")
    print("=" * 60)
    
    test_dir = tempfile.mkdtemp()
    try:
        bdmv_path = create_mock_bdj_disc(test_dir)
        
        # Test main parser with BD-J integration
        parser = BlurayParser(bdmv_path)
        
        print(f"有效蓝光结构: {'✅ 是' if parser.is_valid_bluray() else '❌ 否'}")
        print(f"BD-J 菜单支持: {'✅ 是' if parser.has_bdj_menus() else '❌ 否'}")
        
        # Get all playlists (including BD-J applications)
        playlists = parser.get_playlists()
        print(f"\n发现 {len(playlists)} 个播放列表/应用:")
        
        for i, playlist in enumerate(playlists, 1):
            menu_type = playlist.get('menu_type', '未知')
            type_name = {
                'bdj_application': 'BD-J 应用',
                'standard_playlist': '标准播放列表',
                'unknown': '未知类型'
            }.get(menu_type, menu_type)
            
            print(f"\n{i}. {playlist['name']} [{type_name}]")
            print(f"   大小: {playlist['size'] / 1024:.1f} KB")
            print(f"   菜单项: {len(playlist.get('menu_items', []))}")
            
            if menu_type == 'bdj_application':
                jar_files = playlist.get('jar_files', [])
                print(f"   JAR 文件: {len(jar_files)}")
                for jar in jar_files:
                    features = jar['menu_content']['estimated_features']
                    print(f"     - {jar['name']}: {', '.join(features)}")
    
    finally:
        shutil.rmtree(test_dir)


def demo_bdj_menu_navigation():
    """Demonstrate BD-J menu navigation"""
    print("\n" + "=" * 60)
    print("BD-J 菜单导航演示")
    print("=" * 60)
    
    test_dir = tempfile.mkdtemp()
    try:
        bdmv_path = create_mock_bdj_disc(test_dir)
        parser = BlurayParser(bdmv_path)
        navigator = BlurayMenuNavigator()
        
        # Get BD-J applications
        bdj_apps = parser.get_bdj_applications()
        
        if bdj_apps:
            # Load first BD-J application
            bdj_app = bdj_apps[0]
            navigator.set_bdj_application(bdj_app)
            
            print(f"加载 BD-J 应用: {bdj_app['bdjo_name']}")
            print(f"BD-J 模式: {'✅ 是' if navigator.is_bdj_mode() else '❌ 否'}")
            
            # Demonstrate navigation
            print("\n菜单导航演示:")
            for i in range(len(navigator.current_menu_items)):
                current_item = navigator.current_menu_items[navigator.selected_item]
                indicator = "🎮 ► " if navigator.is_bdj_mode() else "► "
                print(f"  {indicator}{current_item['title']}")
                
                if i < len(navigator.current_menu_items) - 1:
                    navigator.navigate_down()
            
            # Test menu selection
            print(f"\n当前选择: {navigator.select_current()['title']}")
            
            # Demonstrate switching to standard mode
            print("\n切换到标准菜单模式...")
            navigator.switch_to_standard_menu()
            print(f"BD-J 模式: {'✅ 是' if navigator.is_bdj_mode() else '❌ 否'}")
            print(f"历史记录中的菜单数: {len(navigator.menu_history)}")
    
    finally:
        shutil.rmtree(test_dir)


def demo_bdj_menu_actions():
    """Demonstrate BD-J menu action types"""
    print("\n" + "=" * 60)
    print("BD-J 菜单动作演示")
    print("=" * 60)
    
    test_dir = tempfile.mkdtemp()
    try:
        bdmv_path = create_mock_bdj_disc(test_dir)
        parser = BlurayParser(bdmv_path)
        
        bdj_apps = parser.get_bdj_applications()
        
        if bdj_apps:
            for app in bdj_apps:
                print(f"\nBD-J 应用: {app['bdjo_name']}")
                print("支持的动作类型:")
                
                action_descriptions = {
                    'bdj_play_main': '播放主要内容',
                    'bdj_interactive_menu': '交互式菜单体验',
                    'bdj_chapters': '智能章节导航',
                    'bdj_special': '特殊功能和游戏',
                    'bdj_settings': '高级设置选项',
                    'fallback_menu': '标准菜单切换'
                }
                
                for item in app['menu_items']:
                    action = item['action']
                    description = action_descriptions.get(action, '未知动作')
                    print(f"  • {item['title']}: {description}")
    
    finally:
        shutil.rmtree(test_dir)


def main():
    """Main demonstration function"""
    print("🎮 BD-J (Blu-ray Disc Java) 支持演示")
    print("此演示展示了新增的 BD-J 原生菜单支持功能")
    
    # Run all demonstrations
    demo_bdj_detection()
    demo_bdj_parser_integration()
    demo_bdj_menu_navigation()
    demo_bdj_menu_actions()
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    print("\nBD-J 支持功能包括:")
    print("✅ 自动检测 BD-J 应用")
    print("✅ 解析 BDJO 和 JAR 文件")
    print("✅ 智能菜单结构识别")
    print("✅ BD-J 与标准菜单切换")
    print("✅ 交互式菜单导航")
    print("✅ 特殊功能和设置访问")
    print("\n注意: 完整的 BD-J 支持需要 Java 运行时环境")
    print("当前实现提供了 BD-J 菜单的检测和基础导航功能")


if __name__ == "__main__":
    main()