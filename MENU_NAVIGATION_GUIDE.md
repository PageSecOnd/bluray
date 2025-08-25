# Blu-ray Menu Navigation Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Blu-ray Menu Player                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   File Menu     │  │  Playlist Tree  │  │ Video Files  │ │
│  │ • Open Disc     │  │ • 00001.mpls    │  │ • 00000.m2ts │ │
│  │ • Open Folder   │  │ • 00002.mpls    │  │ • 00001.m2ts │ │
│  │ • Exit          │  │ • 00000.mpls    │  │ • 00002.m2ts │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Menu Navigation                          │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │  ► 播放全部                                         ││ │
│  │  │    章节 1                                           ││ │
│  │  │    章节 2                                           ││ │
│  │  │    章节 3                                           ││ │
│  │  │    ...                                              ││ │
│  │  │    特殊功能                                         ││ │
│  │  │    返回主菜单                                       ││ │
│  │  └─────────────────────────────────────────────────────┘│ │
│  │  [↑] [↓] [选择] [返回] [主菜单]                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            [播放] [停止] [全屏]                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  Status: 已加载菜单: 00001                                   │
└─────────────────────────────────────────────────────────────┘
```

## Menu Navigation Flow

```
Main Playlist (00001.mpls)
├── 播放全部 ──────────────────► Play main video content
├── 章节 1 ───────────────────► Play chapter 1
├── 章节 2 ───────────────────► Play chapter 2
├── 章节 3 ───────────────────► Play chapter 3
├── ...
├── 特殊功能 ─┐
│             ├─► Special Features Submenu
│             │   ├── 花絮视频 ───► Play bonus content
│             │   ├── 制作特辑 ───► Play making-of
│             │   ├── 导演评论 ───► Play commentary
│             │   └── 返回 ──────► Back to main menu
│             │
└── 返回主菜单 ──────────────────► Go to main menu
```

## Menu Types and Structure

### Small Playlist (< 1KB) - Main Menu
```
播放主要内容 ──► play_main
章节选择 ────► chapters ──┐
设置 ────────► settings   │
                         │
        ┌────────────────┘
        ▼
    Chapter Menu
    ├── 章节 1 ──► play_chapter(1)
    ├── 章节 2 ──► play_chapter(2)
    ├── 章节 3 ──► play_chapter(3)
    └── 返回 ────► back
```

### Large Playlist (> 1KB) - Main Content with Chapters
```
播放全部 ────► play_all
章节 1 ──────► play_chapter(1)
章节 2 ──────► play_chapter(2)
章节 3 ──────► play_chapter(3)
...
章节 N ──────► play_chapter(N)
特殊功能 ────► special
返回主菜单 ──► main_menu
```

## Keyboard Controls

- **↑/↓ Arrow Keys**: Navigate menu items
- **Enter**: Select current menu item
- **Escape**: Go back to previous menu
- **Home**: Go to main menu
- **Mouse**: Click menu items or buttons

## Implementation Classes

```
BlurayParser
├── is_valid_bluray()
├── get_playlists() ──────► Enhanced with menu parsing
├── get_video_files()
├── _parse_playlist_menu() ► NEW: Intelligent menu extraction
└── get_main_playlist() ──► NEW: Get primary playlist

BlurayMenuNavigator
├── set_playlist()
├── navigate_up()
├── navigate_down()
├── select_current()
├── go_back()
└── menu_history[] ──────► Track navigation history

BlurayMenuPlayer
├── setup_ui() ─────────► Enhanced with menu components
├── on_playlist_double_click() ► Updated for menu loading
├── menu_navigate_up()
├── menu_navigate_down()
├── menu_select_current()
├── execute_menu_action() ► NEW: Handle menu selections
└── show_*_menu() ──────► Various submenu displays
```

This architecture provides a complete, user-friendly Blu-ray menu navigation experience that closely mimics traditional Blu-ray player behavior.