# Blu-ray Menu Player / 蓝光菜单播放器

一个用 Python 编写的 Windows 蓝光原盘菜单播放软件。

## 功能特性

- 🎬 支持直接播放蓝光原盘菜单
- 💿 自动检测系统中的蓝光光盘
- 📁 支持从文件夹加载蓝光结构
- 🎮 图形化用户界面，操作简单
- 🎵 支持视频和音频播放
- 🖥️ 全屏播放支持
- 🔍 自动解析 BDMV 结构

## 系统要求

- Windows 操作系统（推荐 Windows 10 或更高版本）
- Python 3.7 或更高版本
- VLC Media Player（用于视频播放）

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 VLC Media Player

从官网下载并安装 VLC Media Player：https://www.videolan.org/vlc/

### 3. 运行程序

```bash
python bluray_player.py
```

或者安装为系统包：

```bash
pip install .
bluray-player
```

## 使用说明

### 加载蓝光光盘

1. **从光驱加载**：
   - 点击菜单 "文件" → "打开蓝光光盘"
   - 选择包含蓝光光盘的光驱
   - 程序会自动检测并加载蓝光结构

2. **从文件夹加载**：
   - 点击菜单 "文件" → "打开蓝光文件夹"
   - 选择包含 BDMV 文件夹的目录
   - 程序会解析蓝光文件结构

### 播放控制

- **播放列表**：左侧显示所有可用的播放列表文件(.mpls)
- **视频文件**：右侧显示所有视频流文件(.m2ts)
- **双击播放**：双击任意项目开始播放
- **控制按钮**：使用播放、暂停、停止按钮控制播放
- **全屏模式**：点击全屏按钮进入全屏播放

## 项目结构

```
bluray/
├── bluray_player.py    # 主程序文件
├── requirements.txt    # Python 依赖列表
├── setup.py           # 安装脚本
└── README.md          # 项目说明
```

## 技术实现

### 蓝光结构解析

程序支持标准的 Blu-ray BDMV 目录结构：

```
BDMV/
├── PLAYLIST/          # 播放列表文件 (.mpls)
├── STREAM/           # 视频流文件 (.m2ts)
├── CLIPINF/          # 片段信息文件 (.clpi)
└── ...
```

### 核心组件

- **BlurayParser**: 解析蓝光光盘结构
- **BlurayMenuPlayer**: 主应用程序界面
- **VLC 集成**: 使用 python-vlc 进行媒体播放

## 依赖库说明

- `python-vlc`: VLC 媒体播放器的 Python 绑定
- `Pillow`: 图像处理库（用于界面图标等）
- `tkinter`: Python 内置 GUI 库

## 已知限制

1. 目前主要支持基本的视频文件播放
2. 复杂的蓝光菜单交互功能正在开发中
3. 某些加密的蓝光光盘可能无法正常播放

## 故障排除

### VLC 相关问题

如果遇到 VLC 初始化错误：
1. 确保已安装 VLC Media Player
2. 检查 python-vlc 包是否正确安装
3. 尝试重新安装 VLC 和 python-vlc

### 光盘检测问题

如果无法检测到蓝光光盘：
1. 确保光盘已正确插入光驱
2. 检查光驱是否支持蓝光光盘
3. 尝试使用"打开文件夹"功能加载光盘内容

## 开发计划

- [ ] 完整的蓝光菜单导航支持
- [ ] 字幕显示功能
- [ ] 多音轨选择
- [ ] 章节导航
- [ ] 播放历史记录
- [ ] 自定义播放设置

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。
