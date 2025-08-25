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
        
        self.setup_ui()
        self.setup_vlc()
        
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
        
        # Playlist frame
        playlist_frame = ttk.LabelFrame(content_frame, text="播放列表")
        playlist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Playlist treeview
        self.playlist_tree = ttk.Treeview(playlist_frame, columns=("size",), show="tree headings")
        self.playlist_tree.heading("#0", text="名称")
        self.playlist_tree.heading("size", text="大小")
        self.playlist_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.playlist_tree.bind("<Double-1>", self.on_playlist_double_click)
        
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
                self.playlist_tree.insert("", "end", text=playlist['name'], 
                                        values=(f"{size_mb:.1f} MB",), 
                                        tags=(playlist['path'],))
            
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
        item = self.playlist_tree.selection()[0]
        playlist_path = self.playlist_tree.item(item, "tags")[0]
        self.status_var.set(f"播放列表: {os.path.basename(playlist_path)}")
        # TODO: Parse playlist and play main video
        
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