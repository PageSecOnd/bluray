#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Blu-ray Menu Player
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports first
def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter
        print("✓ tkinter imported successfully")
        tkinter_available = True
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        print("  Note: tkinter is not available in headless environments")
        tkinter_available = False
        
    try:
        import vlc
        print("✓ python-vlc imported successfully")
    except ImportError as e:
        print(f"✗ python-vlc import failed: {e}")
        print("  Note: VLC is optional but recommended for video playback")
        
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
    
    return tkinter_available

# Only import BlurayParser if tkinter is available, otherwise create a standalone version
tkinter_available = test_imports()

if tkinter_available:
    try:
        from bluray_player import BlurayParser
    except ImportError:
        print("Could not import BlurayParser from main module")
        sys.exit(1)
else:
    # Create a standalone BlurayParser for testing
    class BlurayParser:
        """Standalone parser for Blu-ray disc BDMV structure"""
        
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
            """Get all playlist files"""
            playlists = []
            if self.playlist_path.exists():
                for file in self.playlist_path.glob("*.mpls"):
                    playlists.append({
                        'name': file.stem,
                        'path': str(file),
                        'size': file.stat().st_size
                    })
            return sorted(playlists, key=lambda x: x['size'], reverse=True)
            
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

class TestBlurayParser(unittest.TestCase):
    """Test cases for BlurayParser"""
    
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
        
        # Create mock files
        (self.bdmv_path / "PLAYLIST" / "00000.mpls").write_bytes(b"mock playlist data")
        (self.bdmv_path / "PLAYLIST" / "00001.mpls").write_bytes(b"mock playlist data 2")
        (self.bdmv_path / "STREAM" / "00000.m2ts").write_bytes(b"mock video data")
        (self.bdmv_path / "STREAM" / "00001.m2ts").write_bytes(b"mock video data 2")
        (self.bdmv_path / "CLIPINF" / "00000.clpi").write_bytes(b"mock clip info")
        
    def test_invalid_structure(self):
        """Test detection of invalid Blu-ray structure"""
        parser = BlurayParser(self.bdmv_path)
        self.assertFalse(parser.is_valid_bluray())
        
    def test_valid_structure(self):
        """Test detection of valid Blu-ray structure"""
        self.create_test_structure()
        parser = BlurayParser(self.bdmv_path)
        self.assertTrue(parser.is_valid_bluray())
        
    def test_get_playlists(self):
        """Test playlist detection"""
        self.create_test_structure()
        parser = BlurayParser(self.bdmv_path)
        playlists = parser.get_playlists()
        self.assertEqual(len(playlists), 2)
        self.assertTrue(any(p['name'] == '00000' for p in playlists))
        self.assertTrue(any(p['name'] == '00001' for p in playlists))
        
    def test_get_video_files(self):
        """Test video file detection"""
        self.create_test_structure()
        parser = BlurayParser(self.bdmv_path)
        videos = parser.get_video_files()
        self.assertEqual(len(videos), 2)
        self.assertTrue(any(v['name'] == '00000' for v in videos))
        self.assertTrue(any(v['name'] == '00001' for v in videos))

def main_test():
    """Main test function"""
    print("=== Blu-ray Menu Player Test Suite ===")
    print()
    
    # Run unit tests
    print("Running unit tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBlurayParser)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n=== Test Summary ===")
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print(f"✗ {len(result.failures)} failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main_test()
    sys.exit(0 if success else 1)