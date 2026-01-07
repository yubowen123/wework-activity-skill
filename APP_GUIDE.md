# 企业微信活跃度管理系统 - 桌面应用指南

集成 Web 界面、后端 API 和 RPA 自动化的完整桌面应用程序

---

## 📦 应用版本

### 开发版
- **gui_app.py** - 基础 GUI 版本
- **gui_app_tray.py** - 带系统托盘的增强版（推荐）

### 发布版
- **WeWorkActivity.app** - 打包后的 macOS 应用程序
- **企业微信活跃度管理-v1.0.0.dmg** - macOS 安装包

---

## 🚀 快速开始

### 方式 1：直接运行（开发环境）

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 运行基础版本
python gui_app.py

# 运行带托盘版本（推荐）
python gui_app_tray.py
```

**前置条件**:
- ✅ 已安装依赖：`pip install -r requirements.txt`
- ✅ 前端服务正在运行（推荐）：`cd frontend && npm run dev`
- ⚠️  如果前端未运行，应用会使用后端默认页面

### 方式 2：运行打包后的应用

```bash
# 打开应用
open dist/WeWorkActivity.app

# 或者双击 WeWorkActivity.app 图标
```

---

## 🔧 打包应用

### 步骤 1：安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装所有依赖（包括 GUI 和打包工具）
pip install -r requirements.txt
```

### 步骤 2：构建前端（可选但推荐）

```bash
cd frontend
npm install
npm run build
cd ..
```

构建后的文件会被打包到应用中，应用将使用本地文件而不依赖前端开发服务器。

### 步骤 3：生成图标（自动）

图标会在打包时自动生成，也可以手动生成：

```bash
python create_icon.py
```

### 步骤 4：打包应用

```bash
# 一键打包
./build_app.sh
```

打包脚本会：
1. 清理旧的构建文件
2. 检查并构建前端
3. 生成应用图标
4. 使用 PyInstaller 打包
5. 创建 .app 应用程序

**输出**:
- `dist/WeWorkActivity.app` - macOS 应用程序

### 步骤 5：创建 DMG 安装包（可选）

```bash
./create_dmg.sh
```

**输出**:
- `dist/企业微信活跃度管理-v1.0.0.dmg` - DMG 安装镜像

---

## 📱 应用功能

### 自动启动的服务

当应用启动时，会自动启动以下服务：

1. **FastAPI 后端** (端口 8000)
   - 提供 RESTful API
   - 数据库管理
   - 业务逻辑处理

2. **RPA 调度器**
   - 自动执行消息采集
   - 自动执行规则检查
   - 后台定时任务

3. **Web 界面**
   - 内嵌浏览器显示 Vue 界面
   - 完整的管理功能

### 系统托盘功能

使用 `gui_app_tray.py` 版本时，关闭窗口不会退出应用，而是最小化到系统托盘。

**托盘菜单**:
- 📱 显示主界面 - 重新打开窗口
- 🔄 重启 RPA - 重启 RPA 调度器
- ❌ 退出 - 完全退出应用

**使用技巧**:
- 关闭窗口 → 最小化到托盘，后台继续运行
- 点击托盘图标 → 显示菜单
- 退出 → 必须从托盘菜单选择"退出"

---

## ⚙️ 应用配置

### 端口配置

默认端口在 `gui_app_tray.py` 中配置：

```python
self.backend_port = 8000      # 后端 API 端口
self.frontend_port = 5173     # 前端开发服务器端口
```

如需修改，编辑对应的 `.py` 文件。

### RPA 配置

RPA 调度器使用 `rpa/config.py` 中的配置：
- 消息采集间隔：默认 120 分钟
- 规则执行时间：默认每天 09:00
- 调试模式：默认关闭

---

## 🐛 故障排查

### 应用无法启动

**症状**: 双击应用无反应

**解决**:
1. 检查是否允许来自「未识别开发者」的应用
   ```bash
   xattr -cr dist/WeWorkActivity.app
   ```

2. 在「系统偏好设置 → 安全性与隐私」中允许运行

### 窗口无法显示

**症状**: 应用启动但没有窗口

**解决**:
1. 检查控制台日志查看错误
2. 确认端口 8000 和 5173 未被占用
3. 尝试关闭防火墙

### 前端界面空白

**症状**: 窗口打开但是空白页面

**可能原因**:
1. 前端服务未运行且未打包前端文件
2. 后端服务启动失败

**解决**:
1. 开发环境：先运行前端开发服务器
   ```bash
   cd frontend && npm run dev
   ```

2. 打包版本：确保打包前构建了前端
   ```bash
   cd frontend && npm run build
   ```

### RPA 功能异常

**症状**: RPA 任务不执行

**解决**:
1. 检查数据库文件是否存在：`data/wework.db`
2. 查看托盘菜单，尝试"重启 RPA"
3. 检查是否有规则被启用
4. 查看日志输出

### 打包失败

**症状**: `./build_app.sh` 执行失败

**解决**:
1. 确认已安装所有依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 清理缓存重新打包
   ```bash
   rm -rf build dist __pycache__
   ./build_app.sh
   ```

3. 查看详细错误信息，通常是缺少隐藏导入

---

## 📊 应用架构

```
WeWorkActivity.app
├── Contents/
│   ├── MacOS/
│   │   └── WeWorkActivity      # 主可执行文件
│   ├── Resources/
│   │   ├── icon.icns           # 应用图标
│   │   └── ...                 # 其他资源
│   └── Info.plist              # 应用信息
└── (内嵌)
    ├── FastAPI 后端
    ├── RPA 调度器
    ├── SQLite 数据库
    └── 前端文件（如果构建）
```

**启动流程**:
1. 启动可执行文件
2. 初始化 FastAPI 后端（后台线程）
3. 启动 RPA 调度器（后台线程）
4. 创建系统托盘图标
5. 打开 WebView 窗口
6. 加载 Web 界面

---

## 🎨 自定义应用

### 修改应用名称

编辑 `wework_activity.spec`:

```python
app = BUNDLE(
    ...
    name='YourAppName.app',  # 修改这里
    info_plist={
        'CFBundleName': '你的应用名',  # 和这里
        'CFBundleDisplayName': '你的应用显示名',  # 和这里
    },
)
```

### 修改应用图标

1. 编辑 `create_icon.py` 自定义图标样式
2. 运行 `python create_icon.py` 生成新图标
3. 重新打包应用

### 修改窗口大小

编辑 `gui_app_tray.py`:

```python
self.window = webview.create_window(
    ...
    width=1400,    # 修改宽度
    height=900,    # 修改高度
    min_size=(1200, 800),  # 最小尺寸
)
```

---

## 🔐 权限说明

应用可能需要以下权限：

### 辅助功能权限
- **原因**: RPA 自动化需要控制企业微信
- **授予方式**: 系统偏好设置 → 安全性与隐私 → 辅助功能 → 添加应用

### 文件访问权限
- **原因**: 读写数据库和配置文件
- **自动授予**: 首次访问时系统会提示

---

## 📦 分发应用

### 方式 1：直接分发 .app

将 `dist/WeWorkActivity.app` 压缩为 ZIP 文件分发：

```bash
cd dist
zip -r WeWorkActivity.zip WeWorkActivity.app
```

**用户安装**:
1. 解压 ZIP 文件
2. 将 .app 拖动到「应用程序」文件夹
3. 右键打开（首次运行）

### 方式 2：分发 DMG

使用 `./create_dmg.sh` 创建的 DMG 安装包：

```bash
# 分发文件
dist/企业微信活跃度管理-v1.0.0.dmg
```

**用户安装**:
1. 双击 DMG 文件挂载
2. 将应用拖动到「Applications」快捷方式
3. 卸载 DMG
4. 打开「应用程序」启动

---

## 💡 开发技巧

### 调试打包问题

打开控制台模式查看错误：

```python
# 在 gui_app_tray.py 中修改
webview.start(debug=True)  # 开启调试模式

# 或在 .spec 文件中
exe = EXE(
    ...
    console=True,  # 显示控制台窗口
)
```

### 查看打包内容

```bash
# 查看 .app 内容
open dist/WeWorkActivity.app/Contents

# 查看打包的 Python 模块
ls dist/WeWorkActivity.app/Contents/MacOS/
```

### 减小应用体积

1. **排除不必要的模块**（在 .spec 中）:
   ```python
   excludes=[
       'matplotlib',
       'pandas',
       'scipy',
       # 添加其他不需要的模块
   ],
   ```

2. **启用 UPX 压缩**（已启用）:
   ```python
   upx=True,
   ```

---

## 📞 技术支持

**问题反馈**:
- GitHub Issues
- 查看日志文件
- 控制台输出

**常用命令**:
```bash
# 查看应用日志
open dist/WeWorkActivity.app

# 清理重建
rm -rf build dist && ./build_app.sh

# 测试未打包版本
python gui_app_tray.py
```

---

## ✅ 总结

**开发测试**:
```bash
python gui_app_tray.py
```

**打包应用**:
```bash
./build_app.sh
```

**创建安装包**:
```bash
./create_dmg.sh
```

**分发**:
- 开发者：分发 DMG 文件
- 用户：双击安装，拖动到应用程序文件夹

---

**🎉 享受自动化管理的便利！**
