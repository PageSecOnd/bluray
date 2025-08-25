#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for Blu-ray Menu Player
Creates a sample Blu-ray structure and demonstrates the parsing functionality.
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_demo_bluray():
    """Create a demo Blu-ray structure for testing"""
    print("Creating demo Blu-ray structure...")
    
    # Create temporary directory
    demo_dir = Path(tempfile.mkdtemp(prefix="bluray_demo_"))
    bdmv_dir = demo_dir / "BDMV"
    
    # Create directory structure
    (bdmv_dir / "PLAYLIST").mkdir(parents=True)
    (bdmv_dir / "STREAM").mkdir(parents=True)
    (bdmv_dir / "CLIPINF").mkdir(parents=True)
    (bdmv_dir / "AUXDATA").mkdir(parents=True)
    (bdmv_dir / "META").mkdir(parents=True)
    
    # Create mock playlist files
    playlists = [
        ("00000.mpls", b"Mock main playlist data" * 100),  # Main movie
        ("00001.mpls", b"Mock menu playlist data" * 50),   # Menu
        ("00002.mpls", b"Mock bonus playlist data" * 30),  # Bonus content
        ("00800.mpls", b"Mock trailer playlist data" * 20), # Trailer
    ]
    
    for filename, data in playlists:
        (bdmv_dir / "PLAYLIST" / filename).write_bytes(data)
    
    # Create mock video files
    videos = [
        ("00000.m2ts", b"Mock main movie video data" * 1000),  # Main movie
        ("00001.m2ts", b"Mock menu video data" * 100),         # Menu background
        ("00002.m2ts", b"Mock bonus video data" * 500),        # Bonus content
        ("00003.m2ts", b"Mock trailer video data" * 200),      # Trailer
        ("00800.m2ts", b"Mock intro video data" * 50),         # Studio intro
    ]
    
    for filename, data in videos:
        (bdmv_dir / "STREAM" / filename).write_bytes(data)
    
    # Create mock clip info files
    clips = [
        ("00000.clpi", b"Mock clip info for main movie"),
        ("00001.clpi", b"Mock clip info for menu"),
        ("00002.clpi", b"Mock clip info for bonus"),
        ("00003.clpi", b"Mock clip info for trailer"),
        ("00800.clpi", b"Mock clip info for intro"),
    ]
    
    for filename, data in clips:
        (bdmv_dir / "CLIPINF" / filename).write_bytes(data)
    
    # Create index.bdmv file (main index)
    (bdmv_dir / "index.bdmv").write_bytes(b"Mock Blu-ray index file")
    
    # Create MovieObject.bdmv file
    (bdmv_dir / "MovieObject.bdmv").write_bytes(b"Mock movie object file")
    
    print(f"Demo Blu-ray created at: {demo_dir}")
    print(f"BDMV path: {bdmv_dir}")
    
    return str(demo_dir), str(bdmv_dir)

def demo_parser():
    """Demonstrate the BlurayParser functionality"""
    print("\n=== Blu-ray Parser Demo ===")
    
    # Import the parser (standalone version for testing)
    from test_bluray import BlurayParser
    
    # Create demo structure
    demo_root, bdmv_path = create_demo_bluray()
    
    try:
        # Initialize parser
        parser = BlurayParser(bdmv_path)
        
        # Test validation
        print(f"\nTesting Blu-ray structure validation...")
        is_valid = parser.is_valid_bluray()
        print(f"Is valid Blu-ray: {'✓ Yes' if is_valid else '✗ No'}")
        
        if is_valid:
            # Get playlists
            print(f"\nPlaylists found:")
            playlists = parser.get_playlists()
            for i, playlist in enumerate(playlists, 1):
                size_mb = playlist['size'] / 1024
                print(f"  {i}. {playlist['name']}.mpls ({size_mb:.1f} KB)")
                print(f"     Path: {playlist['path']}")
            
            # Get video files
            print(f"\nVideo files found:")
            videos = parser.get_video_files()
            for i, video in enumerate(videos, 1):
                size_mb = video['size'] / 1024
                print(f"  {i}. {video['name']}.m2ts ({size_mb:.1f} KB)")
                print(f"     Path: {video['path']}")
            
            # Analyze structure
            print(f"\n=== Structure Analysis ===")
            print(f"Total playlists: {len(playlists)}")
            print(f"Total video files: {len(videos)}")
            
            # Identify likely main content
            if playlists:
                main_playlist = playlists[0]  # Largest playlist
                print(f"Likely main playlist: {main_playlist['name']}.mpls")
            
            if videos:
                main_video = videos[0]  # Largest video
                print(f"Likely main movie: {main_video['name']}.m2ts")
        
    finally:
        # Clean up
        print(f"\nCleaning up demo files...")
        shutil.rmtree(demo_root)
        print("Demo completed.")

def demo_gui_features():
    """Demonstrate GUI features (conceptual)"""
    print("\n=== GUI Features Demo ===")
    print("GUI features that would be available:")
    print("1. ✓ Automatic drive detection")
    print("2. ✓ Folder browser for Blu-ray directories")
    print("3. ✓ Playlist display with file sizes")
    print("4. ✓ Video file listing")
    print("5. ✓ Double-click to play functionality")
    print("6. ✓ Play/pause/stop controls")
    print("7. ✓ Fullscreen toggle")
    print("8. ✓ Status bar with current operation")
    print("9. ✓ Menu bar with file operations")
    print("10. ✓ Error handling and user feedback")

def demo_windows_integration():
    """Show Windows-specific features"""
    print("\n=== Windows Integration Demo ===")
    print("Windows-specific features:")
    print("1. ✓ Automatic CD/DVD drive detection")
    print("2. ✓ Windows path handling")
    print("3. ✓ Batch file launcher (run.bat)")
    print("4. ✓ VLC integration for media playback")
    print("5. ✓ Chinese language interface support")
    
    # Try to detect drives (will work on Windows)
    try:
        import string
        import platform
        
        if platform.system() == "Windows":
            print("\nDrive detection test:")
            for letter in string.ascii_uppercase[:5]:  # Check first 5 letters
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    print(f"  Found drive: {letter}:")
        else:
            print("(Drive detection is Windows-specific)")
    except Exception as e:
        print(f"Drive detection test failed: {e}")

def main():
    """Main demo function"""
    print("🎬 Blu-ray Menu Player Demonstration 🎬")
    print("========================================")
    
    # Demo core parsing functionality
    demo_parser()
    
    # Demo GUI features
    demo_gui_features()
    
    # Demo Windows integration
    demo_windows_integration()
    
    print("\n✨ Demo completed! ✨")
    print("\nTo run the actual application:")
    print("- On Windows: run.bat")
    print("- Or directly: python launcher.py")
    print("- Or main app: python bluray_player.py")

if __name__ == "__main__":
    main()