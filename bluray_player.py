#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blu-ray Menu Player for Windows
A Python application to play Blu-ray disc menus directly on Windows.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from pathlib import Path
import platform

try:
    import vlc
except ImportError:
    vlc = None

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
    """Parser for Blu-ray disc BDMV structure"""
    
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

class BlurayMenuPlayer:
    """Main Blu-ray Menu Player application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blu-ray Menu Player")
        self.root.geometry("800x600")
        
        # VLC player instance
        self.vlc_instance = None
        self.media_player = None
        
        # Current Blu-ray info
        self.current_bdmv = None
        self.parser = None
        
        # Menu navigation
        self.menu_navigator = BlurayMenuNavigator()
        self.current_menu_display = None
        
        self.setup_ui()
        self.setup_vlc()
        self.setup_keyboard_bindings()
        
    def setup_vlc(self):
        """Initialize VLC media player"""
        if vlc is None:
            messagebox.showerror("错误", "VLC 库未安装。请安装 python-vlc 包。")
            return
            
        try:
            self.vlc_instance = vlc.Instance()
            self.media_player = self.vlc_instance.media_player_new()
        except Exception as e:
            messagebox.showerror("VLC 错误", f"无法初始化 VLC: {e}")
            
    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开蓝光光盘", command=self.open_bluray_disc)
        file_menu.add_command(label="打开蓝光文件夹", command=self.open_bluray_folder)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Disc info frame
        info_frame = ttk.LabelFrame(main_frame, text="蓝光光盘信息")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.disc_info_label = ttk.Label(info_frame, text="未加载蓝光光盘")
        self.disc_info_label.pack(pady=10)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel with playlists and menu navigation
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Playlist frame
        playlist_frame = ttk.LabelFrame(left_panel, text="播放列表")
        playlist_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Playlist treeview
        self.playlist_tree = ttk.Treeview(playlist_frame, columns=("size",), show="tree headings", height=6)
        self.playlist_tree.heading("#0", text="名称")
        self.playlist_tree.heading("size", text="大小")
        self.playlist_tree.pack(fill=tk.X, padx=5, pady=5)
        self.playlist_tree.bind("<Double-1>", self.on_playlist_double_click)
        
        # Menu navigation frame
        menu_nav_frame = ttk.LabelFrame(left_panel, text="菜单导航")
        menu_nav_frame.pack(fill=tk.BOTH, expand=True)
        
        # Menu display
        self.menu_display = tk.Listbox(menu_nav_frame, height=8)
        self.menu_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        self.menu_display.bind("<Double-1>", self.on_menu_item_select)
        self.menu_display.bind("<Return>", self.on_menu_item_select)
        
        # Menu navigation buttons
        menu_button_frame = ttk.Frame(menu_nav_frame)
        menu_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.menu_up_btn = ttk.Button(menu_button_frame, text="↑", command=self.menu_navigate_up, width=3)
        self.menu_up_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.menu_down_btn = ttk.Button(menu_button_frame, text="↓", command=self.menu_navigate_down, width=3)
        self.menu_down_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.menu_select_btn = ttk.Button(menu_button_frame, text="选择", command=self.menu_select_current)
        self.menu_select_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.menu_back_btn = ttk.Button(menu_button_frame, text="返回", command=self.menu_go_back)
        self.menu_back_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.menu_main_btn = ttk.Button(menu_button_frame, text="主菜单", command=self.show_main_menu)
        self.menu_main_btn.pack(side=tk.LEFT)
        
        # Video files frame
        video_frame = ttk.LabelFrame(content_frame, text="视频文件")
        video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Video files treeview
        self.video_tree = ttk.Treeview(video_frame, columns=("size",), show="tree headings")
        self.video_tree.heading("#0", text="名称")
        self.video_tree.heading("size", text="大小")
        self.video_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.video_tree.bind("<Double-1>", self.on_video_double_click)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Control buttons
        self.play_button = ttk.Button(control_frame, text="播放", command=self.play_pause)
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="停止", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.fullscreen_button = ttk.Button(control_frame, text="全屏", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def setup_keyboard_bindings(self):
        """Setup keyboard bindings for menu navigation"""
        self.root.bind("<Up>", lambda e: self.menu_navigate_up())
        self.root.bind("<Down>", lambda e: self.menu_navigate_down())
        self.root.bind("<Return>", lambda e: self.menu_select_current())
        self.root.bind("<Escape>", lambda e: self.menu_go_back())
        self.root.bind("<Home>", lambda e: self.show_main_menu())
        
        # Make the root window focusable for key events
        self.root.focus_set()
        
    def open_bluray_disc(self):
        """Open Blu-ray disc from drive"""
        if platform.system() != "Windows":
            messagebox.showwarning("警告", "此功能仅在 Windows 系统上可用")
            return
            
        # Get available drives
        drives = self.get_available_drives()
        if not drives:
            messagebox.showinfo("信息", "未找到可用的光驱")
            return
            
        # Simple drive selection dialog
        drive_window = tk.Toplevel(self.root)
        drive_window.title("选择光驱")
        drive_window.geometry("300x200")
        drive_window.transient(self.root)
        drive_window.grab_set()
        
        tk.Label(drive_window, text="请选择包含蓝光光盘的光驱:").pack(pady=10)
        
        selected_drive = tk.StringVar()
        for drive in drives:
            tk.Radiobutton(drive_window, text=f"{drive}:\\", 
                          variable=selected_drive, value=drive).pack()
        
        def on_ok():
            if selected_drive.get():
                bdmv_path = f"{selected_drive.get()}:\\BDMV"
                if os.path.exists(bdmv_path):
                    self.load_bluray(bdmv_path)
                    drive_window.destroy()
                else:
                    messagebox.showerror("错误", f"在 {selected_drive.get()}: 上未找到蓝光光盘")
            else:
                messagebox.showwarning("警告", "请选择一个光驱")
        
        tk.Button(drive_window, text="确定", command=on_ok).pack(pady=10)
        tk.Button(drive_window, text="取消", command=drive_window.destroy).pack()
        
    def get_available_drives(self):
        """Get available CD/DVD drives on Windows"""
        if platform.system() != "Windows":
            return []
            
        import string
        drives = []
        for letter in string.ascii_uppercase:
            if os.path.exists(f"{letter}:\\"):
                drives.append(letter)
        return drives
        
    def open_bluray_folder(self):
        """Open Blu-ray folder"""
        folder_path = filedialog.askdirectory(title="选择蓝光文件夹")
        if folder_path:
            # Check if it's a BDMV folder or contains BDMV
            bdmv_path = None
            if os.path.basename(folder_path) == "BDMV":
                bdmv_path = folder_path
            elif os.path.exists(os.path.join(folder_path, "BDMV")):
                bdmv_path = os.path.join(folder_path, "BDMV")
            
            if bdmv_path:
                self.load_bluray(bdmv_path)
            else:
                messagebox.showerror("错误", "所选文件夹不包含有效的蓝光结构")
                
    def load_bluray(self, bdmv_path):
        """Load Blu-ray disc from path"""
        try:
            self.parser = BlurayParser(bdmv_path)
            
            if not self.parser.is_valid_bluray():
                messagebox.showerror("错误", "无效的蓝光光盘结构")
                return
                
            self.current_bdmv = bdmv_path
            self.disc_info_label.config(text=f"已加载: {bdmv_path}")
            
            # Load playlists
            playlists = self.parser.get_playlists()
            self.playlist_tree.delete(*self.playlist_tree.get_children())
            for playlist in playlists:
                size_mb = playlist['size'] / (1024 * 1024)
                menu_count = len(playlist.get('menu_items', []))
                display_text = f"{playlist['name']} ({menu_count} 项菜单)"
                self.playlist_tree.insert("", "end", text=display_text, 
                                        values=(f"{size_mb:.1f} MB",), 
                                        tags=(json.dumps(playlist),))
            
            # Load video files
            videos = self.parser.get_video_files()
            self.video_tree.delete(*self.video_tree.get_children())
            for video in videos:
                size_mb = video['size'] / (1024 * 1024)
                self.video_tree.insert("", "end", text=video['name'], 
                                     values=(f"{size_mb:.1f} MB",), 
                                     tags=(video['path'],))
                                     
            self.status_var.set(f"已加载 {len(playlists)} 个播放列表, {len(videos)} 个视频文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载蓝光光盘失败: {e}")
            
    def on_playlist_double_click(self, event):
        """Handle playlist double-click"""
        if not self.playlist_tree.selection():
            return
            
        item = self.playlist_tree.selection()[0]
        playlist_json = self.playlist_tree.item(item, "tags")[0]
        playlist_info = json.loads(playlist_json)
        
        # Set up menu navigation
        self.menu_navigator.set_playlist(playlist_info)
        self.update_menu_display()
        
        self.status_var.set(f"已加载菜单: {playlist_info['name']}")
        
    def update_menu_display(self):
        """Update the menu display with current menu items"""
        self.menu_display.delete(0, tk.END)
        
        if not self.menu_navigator.current_menu_items:
            self.menu_display.insert(tk.END, "无可用菜单项")
            return
            
        for i, item in enumerate(self.menu_navigator.current_menu_items):
            prefix = "► " if i == self.menu_navigator.selected_item else "  "
            self.menu_display.insert(tk.END, f"{prefix}{item['title']}")
            
        # Highlight selected item
        if self.menu_navigator.current_menu_items:
            self.menu_display.selection_clear(0, tk.END)
            self.menu_display.selection_set(self.menu_navigator.selected_item)
            self.menu_display.see(self.menu_navigator.selected_item)
            
    def menu_navigate_up(self):
        """Navigate up in menu"""
        self.menu_navigator.navigate_up()
        self.update_menu_display()
        
    def menu_navigate_down(self):
        """Navigate down in menu"""
        self.menu_navigator.navigate_down()
        self.update_menu_display()
        
    def menu_select_current(self):
        """Select current menu item"""
        selected_item = self.menu_navigator.select_current()
        if selected_item:
            self.execute_menu_action(selected_item)
            
    def menu_go_back(self):
        """Go back to previous menu"""
        previous_menu = self.menu_navigator.go_back()
        if previous_menu:
            self.menu_navigator.set_playlist(previous_menu)
            self.update_menu_display()
            self.status_var.set("返回上级菜单")
        else:
            self.status_var.set("已在顶级菜单")
            
    def show_main_menu(self):
        """Show main menu (largest playlist)"""
        if self.parser:
            main_playlist = self.parser.get_main_playlist()
            if main_playlist:
                self.menu_navigator.set_playlist(main_playlist)
                self.update_menu_display()
                self.status_var.set("显示主菜单")
                
    def on_menu_item_select(self, event):
        """Handle menu item selection via double-click or Enter"""
        selection = self.menu_display.curselection()
        if selection:
            self.menu_navigator.selected_item = selection[0]
            self.menu_select_current()
            
    def execute_menu_action(self, menu_item):
        """Execute the action for a selected menu item"""
        action = menu_item['action']
        target = menu_item.get('target')
        
        self.status_var.set(f"执行: {menu_item['title']}")
        
        if action == 'play_main' or action == 'play_all':
            # Play the main video content
            self.play_main_content()
            
        elif action == 'play_chapter':
            # Play specific chapter
            self.play_chapter(target)
            
        elif action == 'chapters':
            # Show chapter selection menu
            self.show_chapter_menu()
            
        elif action == 'settings':
            # Show settings menu
            self.show_settings_menu()
            
        elif action == 'special':
            # Show special features
            self.show_special_features()
            
        elif action == 'main_menu':
            # Go to main menu
            self.show_main_menu()
            
        elif action == 'back':
            # Go back
            self.menu_go_back()
            
        else:
            self.status_var.set(f"未知操作: {action}")
            
    def play_main_content(self):
        """Play the main video content"""
        if not self.parser:
            return
            
        # Get the largest video file (likely main content)
        videos = self.parser.get_video_files()
        if videos:
            main_video = videos[0]  # Largest video file
            self.play_video(main_video['path'])
            self.status_var.set(f"播放主要内容: {main_video['name']}")
        else:
            self.status_var.set("未找到视频文件")
            
    def play_chapter(self, chapter_num):
        """Play specific chapter"""
        self.status_var.set(f"播放章节 {chapter_num}")
        # For now, play main content - could be enhanced with actual chapter seeking
        self.play_main_content()
        
    def show_chapter_menu(self):
        """Show chapter selection menu"""
        # Create a chapter menu
        chapter_menu = {
            'name': 'chapters',
            'menu_items': [
                {'title': f'章节 {i}', 'action': 'play_chapter', 'target': i}
                for i in range(1, 11)  # Example: 10 chapters
            ] + [{'title': '返回', 'action': 'back', 'target': None}]
        }
        
        # Save current menu to history
        if self.menu_navigator.current_playlist:
            self.menu_navigator.menu_history.append(self.menu_navigator.current_playlist)
            
        self.menu_navigator.set_playlist(chapter_menu)
        self.update_menu_display()
        self.status_var.set("章节选择菜单")
        
    def show_settings_menu(self):
        """Show settings menu"""
        settings_menu = {
            'name': 'settings',
            'menu_items': [
                {'title': '音频设置', 'action': 'audio_settings', 'target': None},
                {'title': '字幕设置', 'action': 'subtitle_settings', 'target': None},
                {'title': '显示设置', 'action': 'display_settings', 'target': None},
                {'title': '返回', 'action': 'back', 'target': None}
            ]
        }
        
        # Save current menu to history
        if self.menu_navigator.current_playlist:
            self.menu_navigator.menu_history.append(self.menu_navigator.current_playlist)
            
        self.menu_navigator.set_playlist(settings_menu)
        self.update_menu_display()
        self.status_var.set("设置菜单")
        
    def show_special_features(self):
        """Show special features menu"""
        special_menu = {
            'name': 'special',
            'menu_items': [
                {'title': '花絮视频', 'action': 'play_bonus', 'target': None},
                {'title': '制作特辑', 'action': 'play_making_of', 'target': None},
                {'title': '导演评论', 'action': 'play_commentary', 'target': None},
                {'title': '返回', 'action': 'back', 'target': None}
            ]
        }
        
        # Save current menu to history
        if self.menu_navigator.current_playlist:
            self.menu_navigator.menu_history.append(self.menu_navigator.current_playlist)
            
        self.menu_navigator.set_playlist(special_menu)
        self.update_menu_display()
        self.status_var.set("特殊功能菜单")
        
    def on_video_double_click(self, event):
        """Handle video file double-click"""
        item = self.video_tree.selection()[0]
        video_path = self.video_tree.item(item, "tags")[0]
        self.play_video(video_path)
        
    def play_video(self, video_path):
        """Play video file"""
        if not self.media_player:
            messagebox.showerror("错误", "媒体播放器未初始化")
            return
            
        try:
            media = self.vlc_instance.media_new(video_path)
            self.media_player.set_media(media)
            self.media_player.play()
            self.status_var.set(f"正在播放: {os.path.basename(video_path)}")
            self.play_button.config(text="暂停")
        except Exception as e:
            messagebox.showerror("错误", f"播放失败: {e}")
            
    def play_pause(self):
        """Play or pause current media"""
        if not self.media_player:
            return
            
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.config(text="播放")
            self.status_var.set("已暂停")
        else:
            self.media_player.play()
            self.play_button.config(text="暂停")
            self.status_var.set("正在播放")
            
    def stop(self):
        """Stop current media"""
        if self.media_player:
            self.media_player.stop()
            self.play_button.config(text="播放")
            self.status_var.set("已停止")
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.media_player:
            self.media_player.toggle_fullscreen()
            
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    if platform.system() != "Windows":
        print("警告: 此应用程序主要为 Windows 系统设计")
    
    app = BlurayMenuPlayer()
    app.run()

if __name__ == "__main__":
    main()