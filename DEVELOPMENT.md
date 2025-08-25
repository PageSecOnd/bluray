# Development Guide / 开发指南

## 项目结构

```
bluray/
├── bluray_player.py    # 主程序 - 包含 GUI 和蓝光解析逻辑
├── launcher.py         # 启动器 - 检查依赖并启动主程序
├── test_bluray.py      # 测试套件 - 单元测试
├── run.bat            # Windows 批处理启动脚本
├── requirements.txt    # Python 依赖
├── setup.py           # 安装脚本
├── README.md          # 用户文档
├── DEVELOPMENT.md     # 开发文档（本文件）
└── .gitignore         # Git 忽略文件
```

## 核心组件

### BlurayParser 类
负责解析蓝光光盘的 BDMV 结构：
- `is_valid_bluray()`: 检查目录结构是否为有效的蓝光格式
- `get_playlists()`: 获取所有播放列表文件 (.mpls) 并解析菜单信息
- `get_video_files()`: 获取所有视频流文件 (.m2ts)
- `_parse_playlist_menu()`: 解析播放列表文件提取菜单结构
- `get_main_playlist()`: 获取主播放列表（通常是最大的文件）

### BlurayMenuNavigator 类
菜单导航状态管理器：
- `set_playlist()`: 设置当前播放列表并初始化菜单
- `navigate_up()` / `navigate_down()`: 菜单项导航
- `select_current()`: 选择当前菜单项
- `go_back()`: 返回上级菜单
- 菜单历史记录管理

### BlurayMenuPlayer 类
主应用程序窗口和逻辑：
- GUI 界面管理
- VLC 播放器集成
- 用户交互处理
- 文件/光盘加载
- 菜单导航UI控制
- 键盘快捷键处理

## 蓝光光盘结构

标准的蓝光光盘包含以下目录结构：

```
BDMV/
├── PLAYLIST/           # 播放列表目录
│   ├── 00000.mpls     # 主要播放列表
│   ├── 00001.mpls     # 其他播放列表
│   └── ...
├── STREAM/            # 视频流目录
│   ├── 00000.m2ts     # 视频文件
│   ├── 00001.m2ts     # 其他视频文件
│   └── ...
├── CLIPINF/           # 片段信息目录
│   ├── 00000.clpi     # 片段信息文件
│   └── ...
├── AUXDATA/           # 辅助数据（可选）
├── META/              # 元数据（可选）
└── BACKUP/            # 备份目录（可选）
```

## 开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/PageSecOnd/bluray.git
cd bluray
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行测试
```bash
python test_bluray.py
```

### 5. 运行程序
```bash
python bluray_player.py
# 或使用启动器
python launcher.py
```

## 扩展功能计划

### 短期目标
- [ ] 实现播放列表解析
- [ ] 添加章节导航
- [ ] 支持字幕显示
- [ ] 多音轨选择

### 中期目标
- [x] 完整菜单导航支持
- [ ] 自定义快捷键
- [ ] 播放历史记录
- [ ] 设置保存/加载

### 长期目标
- [ ] 蓝光菜单动画支持
- [ ] 网络流媒体集成
- [ ] 插件系统
- [ ] 多语言界面

## 贡献指南

### 代码风格
- 使用 UTF-8 编码
- 遵循 PEP 8 风格指南
- 添加适当的注释和文档字符串
- 保持函数简短和专注

### 提交信息格式
```
类型(范围): 简短描述

详细描述（可选）

相关问题: #123
```

类型：
- `feat`: 新功能
- `fix`: 修复错误
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 测试要求
- 新功能必须包含测试
- 确保所有现有测试通过
- 测试覆盖率应保持在 80% 以上

## 已知问题和限制

### 当前限制
1. 只支持基本的视频文件播放
2. ~~复杂的蓝光菜单交互尚未实现~~ **已实现完整菜单导航**
3. 字幕支持有限
4. 加密蓝光光盘支持不完整

### 技术债务
1. 需要更好的错误处理
2. GUI 界面需要优化
3. ~~播放列表解析需要完善~~ **已实现智能播放列表解析**
4. 内存使用优化

## 菜单导航系统架构

### 设计理念
蓝光菜单导航系统设计为模块化、可扩展的架构：

1. **解析层 (BlurayParser)**：
   - 负责读取和解析 BDMV 结构
   - 智能识别播放列表类型
   - 生成菜单项和操作映射

2. **状态管理层 (BlurayMenuNavigator)**：
   - 管理当前菜单状态
   - 处理导航逻辑
   - 维护菜单历史

3. **用户界面层 (BlurayMenuPlayer)**：
   - 显示菜单和控制界面
   - 处理用户输入
   - 执行菜单操作

### 菜单解析算法
基于播放列表文件大小和内容的启发式算法：

- **小文件 (< 1KB)**：主菜单类型，包含基本导航选项
- **大文件 (> 1KB)**：主要内容，根据大小估算章节数量
- **中等文件**：特殊功能或附加内容

### 支持的菜单操作
- `play_main` / `play_all`: 播放主要内容
- `play_chapter`: 播放指定章节
- `chapters`: 显示章节选择菜单
- `settings`: 显示设置菜单
- `special`: 特殊功能菜单
- `back`: 返回上级菜单
- `main_menu`: 返回主菜单

## 调试技巧

### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### VLC 调试
```python
vlc_instance = vlc.Instance("--intf", "dummy", "--verbose", "2")
```

### 测试用例
可以使用以下结构创建测试用的蓝光目录：
```bash
mkdir -p test_bluray/BDMV/{PLAYLIST,STREAM,CLIPINF}
echo "test" > test_bluray/BDMV/PLAYLIST/00000.mpls
echo "test" > test_bluray/BDMV/STREAM/00000.m2ts
echo "test" > test_bluray/BDMV/CLIPINF/00000.clpi
```

## 相关资源

- [Blu-ray Disc Specification](https://www.blu-raydisc.com/)
- [VLC Media Player](https://www.videolan.org/vlc/)
- [Python VLC Bindings](https://wiki.videolan.org/Python_bindings/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)