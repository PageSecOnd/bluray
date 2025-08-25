#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for BD-J (Blu-ray Disc Java) support functionality
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
import struct

# Import the classes to test
from bluray_player import BlurayBDJParser, BlurayMenuNavigator, BlurayParser


class TestBlurayBDJParser(unittest.TestCase):
    """Test BD-J parser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.bdmv_path = Path(self.test_dir) / "BDMV"
        self.jar_path = self.bdmv_path / "JAR"
        self.bdjo_path = self.bdmv_path / "BDJO"
        
        # Create directory structure
        self.bdmv_path.mkdir(parents=True)
        self.jar_path.mkdir()
        self.bdjo_path.mkdir()
        
        self.parser = BlurayBDJParser(self.bdmv_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_bdj_detection_no_files(self):
        """Test BD-J detection with no JAR/BDJO files"""
        self.assertFalse(self.parser.has_bdj_support())
    
    def test_bdj_detection_missing_jar(self):
        """Test BD-J detection with BDJO but no JAR files"""
        # Create a BDJO file
        (self.bdjo_path / "00000.bdjo").write_bytes(b"dummy bdjo content")
        
        self.assertFalse(self.parser.has_bdj_support())
    
    def test_bdj_detection_missing_bdjo(self):
        """Test BD-J detection with JAR but no BDJO files"""
        # Create a JAR file
        (self.jar_path / "00000.jar").write_bytes(b"dummy jar content")
        
        self.assertFalse(self.parser.has_bdj_support())
    
    def test_bdj_detection_with_files(self):
        """Test BD-J detection with both JAR and BDJO files"""
        # Create both JAR and BDJO files
        (self.jar_path / "00000.jar").write_bytes(b"dummy jar content")
        (self.bdjo_path / "00000.bdjo").write_bytes(b"dummy bdjo content")
        
        self.assertTrue(self.parser.has_bdj_support())
    
    def test_bdjo_parsing(self):
        """Test BDJO file parsing"""
        # Create a mock BDJO file with some structured data
        bdjo_data = struct.pack('>HH', 0x1234, 0x5678) + b"dummy content" * 10
        bdjo_file = self.bdjo_path / "12345.bdjo"
        bdjo_file.write_bytes(bdjo_data)
        
        (self.jar_path / "00000.jar").write_bytes(b"dummy jar content")
        
        applications = self.parser.get_bdj_applications()
        
        self.assertEqual(len(applications), 1)
        app = applications[0]
        self.assertEqual(app['bdjo_name'], '12345')
        self.assertEqual(app['menu_type'], 'bdj_application')
        self.assertIsInstance(app['menu_items'], list)
        self.assertGreater(len(app['menu_items']), 0)
    
    def test_multiple_bdj_applications(self):
        """Test parsing multiple BD-J applications"""
        # Create multiple BDJO files
        for i in range(3):
            bdjo_data = struct.pack('>HH', 0x1000 + i, 0x5000 + i) + b"content"
            (self.bdjo_path / f"{i:05d}.bdjo").write_bytes(bdjo_data)
        
        (self.jar_path / "00000.jar").write_bytes(b"dummy jar content")
        
        applications = self.parser.get_bdj_applications()
        
        self.assertEqual(len(applications), 3)
        for app in applications:
            self.assertEqual(app['menu_type'], 'bdj_application')
            self.assertIn('menu_items', app)


class TestBlurayMenuNavigatorBDJ(unittest.TestCase):
    """Test menu navigator with BD-J support"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.navigator = BlurayMenuNavigator()
    
    def test_bdj_mode_detection(self):
        """Test BD-J mode detection"""
        # Initially not in BD-J mode
        self.assertFalse(self.navigator.is_bdj_mode())
        
        # Set standard playlist
        standard_playlist = {
            'name': 'test_playlist',
            'menu_type': 'standard_playlist',
            'menu_items': [{'title': '播放', 'action': 'play', 'target': None}]
        }
        self.navigator.set_playlist(standard_playlist)
        self.assertFalse(self.navigator.is_bdj_mode())
        
        # Set BD-J application
        bdj_app = {
            'name': 'test_bdj',
            'menu_type': 'bdj_application',
            'menu_items': [{'title': 'BD-J 播放', 'action': 'bdj_play', 'target': None}]
        }
        self.navigator.set_playlist(bdj_app)
        self.assertTrue(self.navigator.is_bdj_mode())
    
    def test_bdj_application_setting(self):
        """Test setting BD-J application directly"""
        bdj_app = {
            'name': 'test_bdj',
            'menu_type': 'bdj_application',
            'menu_items': [
                {'title': 'BD-J 主菜单', 'action': 'bdj_main', 'target': None},
                {'title': 'BD-J 设置', 'action': 'bdj_settings', 'target': None}
            ]
        }
        
        self.navigator.set_bdj_application(bdj_app)
        
        self.assertTrue(self.navigator.is_bdj_mode())
        self.assertEqual(self.navigator.current_bdj_app, bdj_app)
        self.assertEqual(len(self.navigator.current_menu_items), 2)
    
    def test_bdj_to_standard_switching(self):
        """Test switching from BD-J to standard menu"""
        # Set up BD-J application
        bdj_app = {
            'name': 'test_bdj',
            'menu_type': 'bdj_application',
            'menu_items': [{'title': 'BD-J 菜单', 'action': 'bdj_action', 'target': None}]
        }
        self.navigator.set_bdj_application(bdj_app)
        self.assertTrue(self.navigator.is_bdj_mode())
        
        # Switch to standard menu
        result = self.navigator.switch_to_standard_menu()
        
        self.assertTrue(result)
        self.assertFalse(self.navigator.is_bdj_mode())
        self.assertIsNone(self.navigator.current_bdj_app)
        # BD-J app should be in history
        self.assertEqual(len(self.navigator.menu_history), 1)
        self.assertEqual(self.navigator.menu_history[0], bdj_app)
    
    def test_menu_navigation_in_bdj_mode(self):
        """Test menu navigation while in BD-J mode"""
        bdj_app = {
            'name': 'test_bdj',
            'menu_type': 'bdj_application',
            'menu_items': [
                {'title': 'BD-J 选项 1', 'action': 'bdj_action1', 'target': None},
                {'title': 'BD-J 选项 2', 'action': 'bdj_action2', 'target': None},
                {'title': 'BD-J 选项 3', 'action': 'bdj_action3', 'target': None}
            ]
        }
        
        self.navigator.set_bdj_application(bdj_app)
        
        # Test navigation
        self.assertEqual(self.navigator.selected_item, 0)
        
        self.navigator.navigate_down()
        self.assertEqual(self.navigator.selected_item, 1)
        
        self.navigator.navigate_down()
        self.assertEqual(self.navigator.selected_item, 2)
        
        # Test wrap-around
        self.navigator.navigate_down()
        self.assertEqual(self.navigator.selected_item, 0)
        
        # Test up navigation
        self.navigator.navigate_up()
        self.assertEqual(self.navigator.selected_item, 2)


class TestBlurayParserBDJ(unittest.TestCase):
    """Test main Blu-ray parser with BD-J integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.bdmv_path = Path(self.test_dir) / "BDMV"
        
        # Create basic BDMV structure
        (self.bdmv_path / "PLAYLIST").mkdir(parents=True)
        (self.bdmv_path / "STREAM").mkdir()
        (self.bdmv_path / "CLIPINF").mkdir()
        
        self.parser = BlurayParser(self.bdmv_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_bdj_detection_integration(self):
        """Test BD-J detection through main parser"""
        # Initially no BD-J support
        self.assertFalse(self.parser.has_bdj_menus())
        
        # Add BD-J files
        jar_path = self.bdmv_path / "JAR"
        bdjo_path = self.bdmv_path / "BDJO"
        jar_path.mkdir()
        bdjo_path.mkdir()
        
        (jar_path / "00000.jar").write_bytes(b"dummy jar content")
        (bdjo_path / "00000.bdjo").write_bytes(b"dummy bdjo content")
        
        # Recreate parser to pick up new structure
        self.parser = BlurayParser(self.bdmv_path)
        self.assertTrue(self.parser.has_bdj_menus())
    
    def test_playlist_with_bdj_integration(self):
        """Test playlist retrieval with BD-J applications"""
        # Add standard playlist
        playlist_file = self.bdmv_path / "PLAYLIST" / "00000.mpls"
        playlist_file.write_bytes(b"dummy playlist content")
        
        # Add BD-J files
        jar_path = self.bdmv_path / "JAR"
        bdjo_path = self.bdmv_path / "BDJO"
        jar_path.mkdir()
        bdjo_path.mkdir()
        
        (jar_path / "00000.jar").write_bytes(b"dummy jar content")
        bdjo_data = struct.pack('>HH', 0x1234, 0x5678) + b"bdjo content"
        (bdjo_path / "12345.bdjo").write_bytes(bdjo_data)
        
        # Recreate parser
        self.parser = BlurayParser(self.bdmv_path)
        playlists = self.parser.get_playlists()
        
        # Should have both BD-J application and standard playlist
        self.assertGreaterEqual(len(playlists), 2)
        
        # Check for BD-J application
        bdj_playlists = [p for p in playlists if p.get('menu_type') == 'bdj_application']
        self.assertEqual(len(bdj_playlists), 1)
        
        # Check for standard playlist
        standard_playlists = [p for p in playlists if p.get('menu_type') == 'standard_playlist']
        self.assertEqual(len(standard_playlists), 1)
    
    def test_bdj_applications_retrieval(self):
        """Test BD-J applications retrieval"""
        # Add BD-J files
        jar_path = self.bdmv_path / "JAR"
        bdjo_path = self.bdmv_path / "BDJO"
        jar_path.mkdir()
        bdjo_path.mkdir()
        
        (jar_path / "00000.jar").write_bytes(b"dummy jar content")
        (bdjo_path / "00000.bdjo").write_bytes(b"dummy bdjo content")
        
        # Recreate parser
        self.parser = BlurayParser(self.bdmv_path)
        bdj_apps = self.parser.get_bdj_applications()
        
        self.assertEqual(len(bdj_apps), 1)
        app = bdj_apps[0]
        self.assertEqual(app['menu_type'], 'bdj_application')
        self.assertIn('menu_items', app)


def run_bdj_tests():
    """Run all BD-J tests"""
    print("Running BD-J support tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add BD-J parser tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBlurayBDJParser))
    
    # Add BD-J menu navigator tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBlurayMenuNavigatorBDJ))
    
    # Add BD-J integration tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBlurayParserBDJ))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_bdj_tests()
    if success:
        print("\n✅ All BD-J support tests passed!")
    else:
        print("\n❌ Some BD-J tests failed!")
        exit(1)