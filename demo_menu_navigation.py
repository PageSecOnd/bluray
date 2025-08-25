#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script to showcase the new Blu-ray menu navigation functionality
"""

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced classes
from test_menu_navigation import BlurayParser, BlurayMenuNavigator

def create_demo_bluray_structure():
    """Create a demo Blu-ray structure for testing"""
    test_dir = tempfile.mkdtemp()
    bdmv_path = Path(test_dir) / "BDMV"
    
    # Create required directories
    (bdmv_path / "PLAYLIST").mkdir(parents=True)
    (bdmv_path / "STREAM").mkdir(parents=True)
    (bdmv_path / "CLIPINF").mkdir(parents=True)
    
    # Create mock files with different sizes to simulate different types of content
    # Small playlist - main menu
    (bdmv_path / "PLAYLIST" / "00000.mpls").write_bytes(b"main menu playlist")
    
    # Large playlist - main movie with chapters
    (bdmv_path / "PLAYLIST" / "00001.mpls").write_bytes(b"x" * 15000)
    
    # Medium playlist - special features
    (bdmv_path / "PLAYLIST" / "00002.mpls").write_bytes(b"y" * 3000)
    
    # Create corresponding video files
    (bdmv_path / "STREAM" / "00000.m2ts").write_bytes(b"main movie video" * 1000)
    (bdmv_path / "STREAM" / "00001.m2ts").write_bytes(b"bonus content video" * 500)
    (bdmv_path / "STREAM" / "00002.m2ts").write_bytes(b"trailer video" * 200)
    
    # Create clip info files
    (bdmv_path / "CLIPINF" / "00000.clpi").write_bytes(b"clip info data")
    (bdmv_path / "CLIPINF" / "00001.clpi").write_bytes(b"clip info data 2")
    
    return str(bdmv_path), test_dir

def demo_menu_navigation():
    """Demonstrate the menu navigation functionality"""
    print("=== Blu-ray Menu Navigation Demo ===\n")
    
    # Create demo structure
    bdmv_path, temp_dir = create_demo_bluray_structure()
    print(f"Created demo Blu-ray structure at: {bdmv_path}")
    
    # Initialize parser
    parser = BlurayParser(bdmv_path)
    
    # Verify structure
    if not parser.is_valid_bluray():
        print("❌ Invalid Blu-ray structure")
        return
    
    print("✅ Valid Blu-ray structure detected\n")
    
    # Get playlists with menu information
    playlists = parser.get_playlists()
    print(f"Found {len(playlists)} playlists:\n")
    
    for i, playlist in enumerate(playlists):
        size_mb = playlist['size'] / 1024
        menu_count = len(playlist['menu_items'])
        print(f"  {i+1}. {playlist['name']} ({size_mb:.1f} KB, {menu_count} menu items)")
        
        # Show menu items for each playlist
        for j, menu_item in enumerate(playlist['menu_items']):
            print(f"     - {menu_item['title']} (action: {menu_item['action']})")
        print()
    
    # Demo menu navigation
    print("=== Menu Navigation Demo ===\n")
    
    # Use the largest playlist (main movie)
    main_playlist = playlists[0]
    print(f"Loading main menu: {main_playlist['name']}\n")
    
    # Initialize menu navigator
    navigator = BlurayMenuNavigator()
    navigator.set_playlist(main_playlist)
    
    # Show current menu state
    def show_menu_state():
        print("Current Menu:")
        for i, item in enumerate(navigator.current_menu_items):
            marker = "► " if i == navigator.selected_item else "  "
            print(f"  {marker}{item['title']}")
        print()
    
    # Demo navigation
    show_menu_state()
    
    print("Navigating down...")
    navigator.navigate_down()
    show_menu_state()
    
    print("Navigating down again...")
    navigator.navigate_down()
    show_menu_state()
    
    print("Selecting current item...")
    selected = navigator.select_current()
    print(f"Selected: {selected['title']} (action: {selected['action']})")
    
    if selected['target']:
        print(f"Target: Chapter {selected['target']}")
    print()
    
    # Demo submenu navigation
    print("=== Submenu Demo ===\n")
    
    # Create a chapter menu
    chapter_menu = {
        'name': 'chapters',
        'menu_items': [
            {'title': f'章节 {i}', 'action': 'play_chapter', 'target': i}
            for i in range(1, 6)
        ] + [{'title': '返回主菜单', 'action': 'back', 'target': None}]
    }
    
    # Save current menu to history and switch to chapter menu
    navigator.menu_history.append(navigator.current_playlist)
    navigator.set_playlist(chapter_menu)
    
    print("Switched to chapter menu:")
    show_menu_state()
    
    print("Navigating to chapter 3...")
    navigator.navigate_down()
    navigator.navigate_down()
    show_menu_state()
    
    print("Going back to main menu...")
    previous_menu = navigator.go_back()
    if previous_menu:
        navigator.set_playlist(previous_menu)
        print("Returned to main menu:")
        show_menu_state()
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("Demo completed successfully! ✅")

if __name__ == "__main__":
    demo_menu_navigation()