# 企业微信活跃度管理系统

基于RPA的企业微信群聊活跃度分析与自动化管理工具。

## 🚀 快速启动

### 方法1：手动启动（推荐首次使用）

#### 1. 安装后端依赖
```bash
pip install -r requirements.txt
```

#### 2. 启动后端服务
```bash
python -m web.app
```
访问: http://localhost:8000

#### 3. 安装前端依赖（新终端）
```bash
cd frontend
npm install
```

#### 4. 启动前端服务
```bash
npm run dev
```
访问: http://localhost:5173

## 📁 项目结构

```
wework-activity-skill/
├── web/                    # 后端
│   ├── app.py             # FastAPI主应用
│   ├── models.py          # 数据库模型
│   ├── database.py        # 数据库连接
│   └── api/               # API路由
├── frontend/              # 前端
│   ├── src/
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── data/                  # 数据目录
│   ├── wework.db         # SQLite数据库
│   ├── exports/          # 导出文件
│   ├── reports/          # 报告
│   └── logs/             # 日志
└── requirements.txt       # Python依赖
```

## 🌟 功能特性

- ✅ **群聊管理** - 可视化管理监控群聊
- ✅ **规则配置** - 灵活的活跃度规则
- ✅ **白名单** - 豁免特定用户
- ✅ **数据分析** - 活跃度可视化
- ✅ **RPA自动化** - 自动导出和移除

## 📖 使用说明

1. 访问 http://localhost:8000 查看后端API文档
2. 访问 http://localhost:5173 使用Web管理界面
3. 点击"健康检查"确认后端连接正常

## ⚙️ 系统要求

- Python 3.8+
- Node.js 16+
- macOS / Windows / Linux

## 📝 待办事项

- [ ] 完整的API实现
- [ ] RPA控制器开发
- [ ] 完整的前端页面
- [ ] Docker部署配置

## 📄 许可证

MIT License
