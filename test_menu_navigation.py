#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Blu-ray menu navigation functionality
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only the classes we need for testing
import json

class BlurayMenuNavigator:
    """Menu navigation state manager for Blu-ray menus"""
    
    def __init__(self):
        self.current_playlist = None
        self.current_menu_items = []
        self.selected_item = 0
        self.menu_history = []
        
    def set_playlist(self, playlist_info):
        """Set current playlist and initialize menu"""
        self.current_playlist = playlist_info
        self.current_menu_items = playlist_info.get('menu_items', [])
        self.selected_item = 0
        
    def navigate_up(self):
        """Navigate to previous menu item"""
        if self.current_menu_items:
            self.selected_item = (self.selected_item - 1) % len(self.current_menu_items)
            return self.selected_item
        return 0
        
    def navigate_down(self):
        """Navigate to next menu item"""
        if self.current_menu_items:
            self.selected_item = (self.selected_item + 1) % len(self.current_menu_items)
            return self.selected_item
        return 0
        
    def select_current(self):
        """Select current menu item"""
        if self.current_menu_items and 0 <= self.selected_item < len(self.current_menu_items):
            return self.current_menu_items[self.selected_item]
        return None
        
    def go_back(self):
        """Go back to previous menu"""
        if self.menu_history:
            return self.menu_history.pop()
        return None

class BlurayParser:
    """Standalone parser for Blu-ray disc BDMV structure with menu support"""
    
    def __init__(self, bdmv_path):
        self.bdmv_path = Path(bdmv_path)
        self.playlist_path = self.bdmv_path / "PLAYLIST"
        self.stream_path = self.bdmv_path / "STREAM"
        self.clipinf_path = self.bdmv_path / "CLIPINF"
        
    def is_valid_bluray(self):
        """Check if the path contains a valid Blu-ray structure"""
        required_dirs = ["PLAYLIST", "STREAM", "CLIPINF"]
        for dir_name in required_dirs:
            if not (self.bdmv_path / dir_name).exists():
                return False
        return True
        
    def get_playlists(self):
        """Get all playlist files with enhanced menu information"""
        playlists = []
        if self.playlist_path.exists():
            for file in self.playlist_path.glob("*.mpls"):
                playlist_info = {
                    'name': file.stem,
                    'path': str(file),
                    'size': file.stat().st_size,
                    'menu_items': self._parse_playlist_menu(file)
                }
                playlists.append(playlist_info)
        return sorted(playlists, key=lambda x: x['size'], reverse=True)
        
    def _parse_playlist_menu(self, playlist_file):
        """Parse playlist file to extract menu information"""
        menu_items = []
        try:
            # Basic menu structure based on file size and common patterns
            file_size = playlist_file.stat().st_size
            
            if file_size < 1000:  # Small playlist - likely a simple menu
                menu_items = [
                    {'title': '播放主要内容', 'action': 'play_main', 'target': None},
                    {'title': '章节选择', 'action': 'chapters', 'target': None},
                    {'title': '设置', 'action': 'settings', 'target': None}
                ]
            else:  # Larger playlist - likely main content with chapters
                # Try to read basic structure
                with open(playlist_file, 'rb') as f:
                    data = f.read(100)  # Read first 100 bytes for basic analysis
                
                # Estimate number of chapters based on file content
                # This is a simplified approach - real MPLS parsing would be more complex
                num_chapters = min(max(file_size // 1000, 1), 20)
                
                menu_items = [{'title': '播放全部', 'action': 'play_all', 'target': None}]
                
                # Add chapter entries
                for i in range(1, num_chapters + 1):
                    menu_items.append({
                        'title': f'章节 {i}',
                        'action': 'play_chapter',
                        'target': i
                    })
                    
                menu_items.extend([
                    {'title': '特殊功能', 'action': 'special', 'target': None},
                    {'title': '返回主菜单', 'action': 'main_menu', 'target': None}
                ])
                
        except Exception:
            # Fallback menu if parsing fails
            menu_items = [
                {'title': '播放', 'action': 'play_main', 'target': None},
                {'title': '返回', 'action': 'back', 'target': None}
            ]
            
        return menu_items
        
    def get_video_files(self):
        """Get all video stream files"""
        videos = []
        if self.stream_path.exists():
            for file in self.stream_path.glob("*.m2ts"):
                videos.append({
                    'name': file.stem,
                    'path': str(file),
                    'size': file.stat().st_size
                })
        return sorted(videos, key=lambda x: x['size'], reverse=True)
        
    def get_main_playlist(self):
        """Get the main playlist (usually the largest one)"""
        playlists = self.get_playlists()
        return playlists[0] if playlists else None

class TestMenuNavigation(unittest.TestCase):
    """Test cases for menu navigation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.bdmv_path = Path(self.test_dir) / "BDMV"
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir)
        
    def create_test_structure(self):
        """Create a mock Blu-ray structure for testing"""
        # Create required directories
        (self.bdmv_path / "PLAYLIST").mkdir(parents=True)
        (self.bdmv_path / "STREAM").mkdir(parents=True)
        (self.bdmv_path / "CLIPINF").mkdir(parents=True)
        
        # Create mock files with different sizes
        (self.bdmv_path / "PLAYLIST" / "00000.mpls").write_bytes(b"small playlist")  # Small file
        (self.bdmv_path / "PLAYLIST" / "00001.mpls").write_bytes(b"x" * 5000)  # Large file
        (self.bdmv_path / "STREAM" / "00000.m2ts").write_bytes(b"mock video data")
        (self.bdmv_path / "CLIPINF" / "00000.clpi").write_bytes(b"mock clip info")
        
    def test_menu_navigator_basic(self):
        """Test basic menu navigation functionality"""
        navigator = BlurayMenuNavigator()
        
        # Test with sample menu
        test_playlist = {
            'name': 'test',
            'menu_items': [
                {'title': '播放主要内容', 'action': 'play_main', 'target': None},
                {'title': '章节选择', 'action': 'chapters', 'target': None},
                {'title': '设置', 'action': 'settings', 'target': None}
            ]
        }
        
        navigator.set_playlist(test_playlist)
        
        # Test initial state
        self.assertEqual(navigator.selected_item, 0)
        self.assertEqual(len(navigator.current_menu_items), 3)
        
        # Test navigation
        navigator.navigate_down()
        self.assertEqual(navigator.selected_item, 1)
        
        navigator.navigate_down()
        self.assertEqual(navigator.selected_item, 2)
        
        # Test wrap-around
        navigator.navigate_down()
        self.assertEqual(navigator.selected_item, 0)
        
        # Test up navigation
        navigator.navigate_up()
        self.assertEqual(navigator.selected_item, 2)
        
    def test_menu_selection(self):
        """Test menu item selection"""
        navigator = BlurayMenuNavigator()
        
        test_playlist = {
            'name': 'test',
            'menu_items': [
                {'title': '播放主要内容', 'action': 'play_main', 'target': None},
                {'title': '章节选择', 'action': 'chapters', 'target': None}
            ]
        }
        
        navigator.set_playlist(test_playlist)
        
        # Test selection
        selected = navigator.select_current()
        self.assertEqual(selected['action'], 'play_main')
        
        navigator.navigate_down()
        selected = navigator.select_current()
        self.assertEqual(selected['action'], 'chapters')
        
    def test_enhanced_playlist_parsing(self):
        """Test enhanced playlist parsing with menu information"""
        self.create_test_structure()
        parser = BlurayParser(self.bdmv_path)
        
        self.assertTrue(parser.is_valid_bluray())
        
        playlists = parser.get_playlists()
        self.assertEqual(len(playlists), 2)
        
        # Check that menu items are parsed
        for playlist in playlists:
            self.assertIn('menu_items', playlist)
            self.assertIsInstance(playlist['menu_items'], list)
            self.assertGreater(len(playlist['menu_items']), 0)
            
        # Test that larger file has more menu items (chapters)
        large_playlist = playlists[0]  # Should be sorted by size, largest first
        small_playlist = playlists[1]
        
        self.assertGreater(large_playlist['size'], small_playlist['size'])
        # Large playlist should have chapter-based menu
        self.assertTrue(any('章节' in item['title'] for item in large_playlist['menu_items']))
        
    def test_menu_history(self):
        """Test menu history functionality"""
        navigator = BlurayMenuNavigator()
        
        main_menu = {
            'name': 'main',
            'menu_items': [{'title': '主菜单', 'action': 'main', 'target': None}]
        }
        
        sub_menu = {
            'name': 'sub',
            'menu_items': [{'title': '子菜单', 'action': 'sub', 'target': None}]
        }
        
        # Set main menu
        navigator.set_playlist(main_menu)
        
        # Add to history and switch to sub menu
        navigator.menu_history.append(main_menu)
        navigator.set_playlist(sub_menu)
        
        # Test going back
        previous = navigator.go_back()
        self.assertEqual(previous['name'], 'main')
        
        # Test empty history
        previous = navigator.go_back()
        self.assertIsNone(previous)

def main_test():
    """Main test function"""
    print("=== Blu-ray Menu Navigation Test Suite ===")
    print()
    
    # Run unit tests
    print("Running menu navigation tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMenuNavigation)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n=== Test Summary ===")
    if result.wasSuccessful():
        print("✓ All menu navigation tests passed!")
    else:
        print(f"✗ {len(result.failures)} failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main_test()
    sys.exit(0 if success else 1)