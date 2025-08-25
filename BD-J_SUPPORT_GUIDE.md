# BD-J (Blu-ray Disc Java) 支持指南

本文档详细介绍了蓝光菜单播放器的 BD-J (Blu-ray Disc Java) 原生菜单支持功能。

## 概述

BD-J 是 Blu-ray 光盘上基于 Java 的交互式菜单系统，提供比传统 HDMV 菜单更丰富的用户体验。我们的实现提供了 BD-J 应用程序的检测、解析和基础导航功能。

## 功能特性

### 🔍 BD-J 检测
- 自动扫描 `BDMV/JAR` 和 `BDMV/BDJO` 目录
- 验证 JAR 和 BDJO 文件的存在
- 在界面上显示 BD-J 支持状态

### 📋 应用程序解析
- 解析 BDJO (BD-J Object) 文件获取应用信息
- 分析 JAR 文件内容推测菜单功能
- 提取应用优先级和基础元数据

### 🎮 交互式菜单
- BD-J 菜单与标准菜单的无缝切换
- 智能菜单项生成基于应用内容分析
- 支持嵌套菜单结构（章节、设置、特殊功能）

### 🖥️ 用户界面集成
- BD-J 状态指示器
- 菜单项的 BD-J 标识（🎮 图标）
- 专用的 BD-J 模式切换按钮

## 技术架构

### 核心组件

#### 1. BlurayBDJParser
```python
class BlurayBDJParser:
    """BD-J 应用程序检测和解析器"""
    
    def has_bdj_support(self) -> bool
    def get_bdj_applications(self) -> List[dict]
    def _parse_bdjo_file(self, bdjo_file) -> dict
    def _extract_jar_menu_info(self, jar_file) -> dict
```

**功能：**
- 检测 BD-J 支持
- 解析 BDJO 文件
- 分析 JAR 文件内容
- 生成菜单结构

#### 2. BlurayMenuNavigator (扩展)
```python
class BlurayMenuNavigator:
    """菜单导航器，支持 BD-J 模式"""
    
    def set_bdj_application(self, bdj_app_info)
    def is_bdj_mode(self) -> bool
    def switch_to_standard_menu(self) -> bool
```

**新增功能：**
- BD-J 模式状态管理
- BD-J 应用程序设置
- 模式切换支持

#### 3. BlurayParser (增强)
```python
class BlurayParser:
    """主解析器，集成 BD-J 支持"""
    
    def has_bdj_menus(self) -> bool
    def get_bdj_applications(self) -> List[dict]
```

**增强功能：**
- BD-J 检测集成
- 统一的播放列表获取（包含 BD-J 应用）

### 数据结构

#### BD-J 应用信息
```python
bdj_app = {
    'bdjo_name': str,           # BDJO 文件名
    'bdjo_path': str,           # BDJO 文件路径
    'size': int,                # 文件大小
    'priority': int,            # 应用优先级
    'menu_type': 'bdj_application',
    'menu_items': List[dict],   # 菜单项列表
    'jar_files': List[dict]     # 关联的 JAR 文件
}
```

#### BD-J 菜单项
```python
menu_item = {
    'title': str,               # 菜单项标题
    'action': str,              # 动作类型 (bdj_*)
    'target': str               # 目标参数
}
```

## BD-J 动作类型

### 标准 BD-J 动作
- `bdj_play_main`: 播放主要内容
- `bdj_interactive_menu`: 交互式菜单体验
- `bdj_chapters`: 章节选择
- `bdj_special`: 特殊功能和游戏
- `bdj_settings`: 高级设置选项
- `fallback_menu`: 切换到标准菜单

### 扩展 BD-J 动作
- `bdj_play_all_chapters`: 播放所有章节
- `bdj_play_chapter`: 播放特定章节
- `bdj_interactive_game`: 交互式游戏
- `bdj_bonus_content`: 花絮内容
- `bdj_making_of`: 制作特辑
- `bdj_gallery`: 图片库
- `bdj_audio_settings`: 音频设置
- `bdj_subtitle_settings`: 字幕设置
- `bdj_display_settings`: 显示设置
- `bdj_network_settings`: 网络设置

## 使用指南

### 基本使用

1. **加载蓝光光盘**：按照标准流程加载包含 BD-J 应用的光盘

2. **BD-J 检测**：界面会自动显示 "BD-J 支持" 状态

3. **切换到 BD-J 模式**：点击 "BD-J" 按钮切换到 Java 菜单模式

4. **菜单导航**：使用方向键或鼠标导航 BD-J 菜单项

5. **返回标准模式**：通过 "返回标准菜单" 选项或再次点击 "BD-J" 按钮

### 键盘快捷键

BD-J 模式支持所有标准键盘快捷键：
- `↑↓`: 菜单导航
- `Enter`: 选择菜单项
- `Esc`: 返回上级菜单
- `Home`: 返回主菜单

### 视觉指示

- **BD-J 状态指示器**：显示 "BD-J 支持" 或 "标准菜单"
- **菜单项标识**：BD-J 菜单项前显示 🎮 图标
- **播放列表标记**：BD-J 应用显示 [BD-J] 标签

## 开发者指南

### 扩展 BD-J 功能

#### 添加新的 BD-J 动作类型

1. 在 `_generate_bdj_menu_items()` 中定义新菜单项
2. 在 `execute_bdj_action()` 中实现动作逻辑
3. 创建相应的子菜单（如需要）

#### 改进 BDJO 解析

当前的 BDJO 解析使用简化方法。要实现完整解析：

1. 研究 BDJO 文件格式规范
2. 实现完整的二进制结构解析
3. 提取更详细的应用元数据

#### 增强 JAR 分析

改进 JAR 文件内容分析：

1. 解析 META-INF/MANIFEST.MF
2. 分析 Java 类文件结构
3. 识别更多菜单功能指示器

### 测试和调试

#### 运行 BD-J 测试

```bash
python test_bdj_support.py
```

#### 运行 BD-J 演示

```bash
python demo_bdj_support.py
```

#### 创建测试光盘结构

使用测试工具创建包含 BD-J 应用的模拟光盘结构进行开发测试。

## 限制和注意事项

### 当前限制

1. **Java 执行**：当前不执行实际的 Java 应用程序
2. **复杂交互**：不支持完整的 BD-J 图形界面
3. **网络功能**：不支持 BD-Live 等网络特性
4. **设备集成**：不支持播放器特定的 BD-J API

### 未来改进

1. **Java 运行时集成**：集成 Java 虚拟机执行 BD-J 应用
2. **图形渲染**：支持 BD-J 图形界面渲染
3. **完整 API 支持**：实现 BD-J 标准 API
4. **性能优化**：优化大型 BD-J 应用的加载和执行

## 兼容性

### 支持的 BD-J 特性

- ✅ BDJO 文件检测和基础解析
- ✅ JAR 文件分析和内容推测
- ✅ 菜单结构生成和导航
- ✅ 与标准菜单的集成
- ✅ 用户界面指示和控制

### 不支持的特性

- ❌ Java 应用程序执行
- ❌ 复杂图形界面渲染
- ❌ BD-Live 网络功能
- ❌ 高级交互式功能
- ❌ 硬件加速图形

## 故障排除

### 常见问题

**Q: BD-J 按钮显示为灰色**
A: 光盘不包含 BD-J 应用程序，或 JAR/BDJO 目录为空

**Q: BD-J 菜单项为空**
A: BDJO 文件解析失败，检查文件格式和权限

**Q: 无法切换回标准菜单**
A: 使用 "返回标准菜单" 选项或重新加载光盘

**Q: BD-J 菜单显示异常**
A: JAR 文件分析失败，将显示默认菜单结构

### 调试技巧

1. 检查控制台输出的 BD-J 解析错误信息
2. 验证光盘的 JAR 和 BDJO 目录结构
3. 使用演示脚本测试 BD-J 功能
4. 运行测试套件验证实现正确性

---

*此文档随着 BD-J 功能的发展而更新。如有问题或建议，请通过 GitHub Issues 反馈。*