# 企业微信活跃度管理系统

> 基于 RPA 的企业微信群聊活跃度分析与自动化管理系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)

## 📖 项目简介

企业微信活跃度管理系统是一个完整的自动化解决方案，用于监控和管理企业微信群聊的用户活跃度。系统通过 RPA（机器人流程自动化）技术，自动采集群聊消息、分析用户活跃度，并根据预设规则自动管理群成员。

### ✨ 核心特性

- 🤖 **RPA 自动化** - 基于 Python 的企业微信客户端自动化控制
- 📊 **活跃度分析** - 统计用户消息数量，识别不活跃成员
- ⚙️ **规则引擎** - 灵活的规则配置，自动执行管理操作
- 🛡️ **白名单机制** - 保护重要成员不被误操作
- 🌐 **Web 管理界面** - 现代化的 Vue 3 + Element Plus 界面
- 🎯 **定时调度** - APScheduler 驱动的定时任务系统
- 📱 **桌面应用** - 可打包为独立的 macOS 应用

## 🎬 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- macOS（RPA 功能针对 macOS 优化）
- 企业微信客户端

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/YOUR_USERNAME/wework-activity-skill.git
cd wework-activity-skill
```

2. **安装后端依赖**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **安装前端依赖**

```bash
cd frontend
npm install
cd ..
```

4. **启动服务**

```bash
# 方式 1：使用桌面应用（推荐）
python gui_app_simple.py

# 方式 2：分别启动后端和前端
# 终端 1 - 启动后端
python -m web.app

# 终端 2 - 启动前端
cd frontend && npm run dev
```

5. **访问系统**

- 前端界面：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📚 功能模块

### 1. 群聊管理
- 添加/删除监控群聊
- 启用/禁用监控
- 配置自动管理选项

### 2. 规则配置
- 设置不活跃天数阈值
- 配置最小消息数要求
- 定时检查时间设置
- 模拟运行/实际执行模式

### 3. 白名单管理
- 添加白名单用户
- 保护重要成员
- 备注管理

### 4. 数据分析
- 用户活跃度统计
- 消息趋势图表
- 活跃排行榜

### 5. RPA 控制（Web 端）
- 测试企业微信连接
- 手动触发消息采集
- 立即执行规则
- 实时状态监控

### 6. 执行历史
- 查看规则执行记录
- 受影响用户列表
- 执行结果和日志

## 🏗️ 系统架构

```
wework-activity-skill/
├── web/                    # 后端（FastAPI）
│   ├── api/               # API 路由
│   ├── models.py          # 数据模型
│   ├── database.py        # 数据库配置
│   └── app.py             # 主应用
├── rpa/                    # RPA 自动化模块
│   ├── wework_automation.py   # 企业微信控制
│   ├── message_collector.py  # 消息采集
│   ├── activity_analyzer.py  # 活跃度分析
│   ├── rule_executor.py      # 规则执行
│   ├── scheduler.py          # 定时调度
│   └── main.py               # 命令行入口
├── frontend/               # 前端（Vue 3）
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   └── router/        # 路由配置
│   └── package.json
├── resources/              # 应用资源
├── data/                   # 数据库文件
├── gui_app_simple.py       # 桌面应用
└── requirements.txt        # Python 依赖
```

## 🔧 配置说明

### 后端配置

编辑 `rpa/config.py`：

```python
# 消息采集间隔（分钟）
MESSAGE_COLLECTION_INTERVAL_MINUTES = 120

# 规则执行时间
RULE_EXECUTION_TIME = '09:00'

# 调试模式
RPA_DEBUG = False
```

### 环境变量

```bash
# API 地址
export API_BASE_URL="http://localhost:8000"

# 调试模式
export RPA_DEBUG="true"

# 日志级别
export LOG_LEVEL="INFO"
```

## 📱 打包桌面应用

### 构建 macOS 应用

```bash
# 1. 构建前端
cd frontend
npm run build
cd ..

# 2. 打包应用
./build_app.sh

# 3. 创建 DMG 安装包
./create_dmg.sh
```

输出文件：
- `dist/WeWorkActivity.app` - macOS 应用
- `dist/企业微信活跃度管理-v1.0.0.dmg` - 安装包

## 🤖 RPA 命令行工具

```bash
# 测试企业微信连接
python -m rpa.main test

# 采集消息
python -m rpa.main collect --chat "群聊名称"

# 执行规则（模拟运行）
python -m rpa.main execute --dry-run

# 启动调度器
python -m rpa.main scheduler

# 从文件导入消息
python -m rpa.main import --chat "群聊名称" --file messages.txt
```

## 📖 详细文档

- [RPA 使用指南](RPA_GUIDE.md)
- [桌面应用指南](APP_GUIDE.md)
- [系统启动说明](STARTUP.md)

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代化的 Python Web 框架
- **SQLAlchemy** - ORM 框架
- **Pydantic** - 数据验证
- **APScheduler** - 定时任务调度
- **Uvicorn** - ASGI 服务器

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - UI 组件库
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **ECharts** - 数据可视化

### RPA 自动化
- **PyAutoGUI** - GUI 自动化
- **pyobjc** - macOS 原生 API
- **OpenCV** - 图像处理
- **pytesseract** - OCR 文字识别

### 桌面应用
- **PyWebView** - Web 视图
- **Pystray** - 系统托盘
- **PyInstaller** - 应用打包

## ⚠️ 注意事项

1. **RPA 功能限制**
   - 目前针对 macOS 优化
   - 需要企业微信客户端已登录
   - 部分 UI 操作需要根据实际界面调整

2. **权限要求**
   - macOS 辅助功能权限（用于 RPA）
   - 文件访问权限（用于数据库和配置）

3. **使用建议**
   - 首次使用建议使用"模拟运行"模式
   - 定期备份数据库文件
   - 重要群聊添加白名单保护

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

由 Claude Code 辅助开发

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)

<!-- aiyou-contact:start -->
## 联系作者 / Contact

扫码添加作者微信，交流使用体验与项目合作。

<img src="docs/assets/wechat-contact.jpg" alt="Glimmer · 光波的个人微信二维码" width="280" />
<!-- aiyou-contact:end -->

如有问题或建议，请提交 Issue。

---

**⭐ 如果这个项目对您有帮助，请给个 Star！**
