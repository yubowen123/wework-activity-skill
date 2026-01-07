# 🎉 企业微信活跃度管理系统 - 启动成功！

## ✅ 系统状态

- ✅ **后端服务**: 正常运行 (端口 8000)
- ✅ **前端服务**: 正常运行 (端口 5173)
- ✅ **数据库**: 已初始化
- ✅ **依赖**: 已安装

## 🔗 访问地址

### 前端界面
http://localhost:5173

**说明**: Web管理界面，提供可视化操作

### 后端API
http://localhost:8000

**说明**: 后端服务首页

### API文档 (Swagger)
http://localhost:8000/docs

**说明**: 交互式API文档，可以直接测试接口

### API文档 (ReDoc)
http://localhost:8000/redoc

**说明**: 另一种风格的API文档

### 健康检查
http://localhost:8000/api/health

**说明**: 检查后端服务是否正常

## 📁 项目结构

```
/Users/gb/wework-activity-skill/
├── web/                    # 后端代码
│   ├── app.py             # FastAPI主应用
│   ├── models.py          # 数据库模型
│   └── database.py        # 数据库连接
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── App.vue
│   │   └── main.js
│   └── package.json
├── data/                  # 数据目录
│   ├── wework.db         # SQLite数据库
│   ├── exports/          # 导出文件
│   ├── reports/          # 报告
│   └── logs/             # 日志
└── README.md             # 项目说明

```

## 🛠️ 常用命令

### 查看后端进程
```bash
ps aux | grep "python3 -m web.app"
```

### 查看前端进程
```bash
ps aux | grep vite
```

### 查看端口监听
```bash
lsof -i :8000  # 后端
lsof -i :5173  # 前端
```

### 停止服务
```bash
# 停止所有后台进程
pkill -f "web.app"
pkill -f "vite"
```

### 重启服务
```bash
# 后端
python3 -m web.app &

# 前端
cd frontend && npm run dev &
```

## 📖 下一步操作

1. **访问前端**: 打开浏览器访问 http://localhost:5173
2. **查看API文档**: 访问 http://localhost:8000/docs
3. **测试健康检查**: 点击前端页面的"健康检查"按钮
4. **阅读文档**: 查看 README.md 了解更多功能

## 💡 快速开始

1. 在前端页面点击"健康检查"按钮，确认后端连接正常
2. 查看API文档了解可用的接口
3. 开始配置监控群聊（功能开发中）

## ⚙️ 配置文件位置

- 后端配置: `web/database.py`
- 前端配置: `frontend/vite.config.js`
- 数据库: `data/wework.db`

## 📝 日志文件

- 后端日志: `backend.log`
- 前端日志: `frontend.log`

## 🔧 故障排查

### 如果后端无法访问
```bash
# 检查进程
ps aux | grep "web.app"

# 查看日志
cat backend.log

# 重启后端
python3 -m web.app &
```

### 如果前端无法访问
```bash
# 检查进程
ps aux | grep vite

# 查看日志
cat frontend.log

# 重启前端
cd frontend && npm run dev &
```

---

**项目创建时间**: $(date)
**Python版本**: $(python3 --version)
**Node.js版本**: $(node --version)

祝使用愉快！ 🚀
