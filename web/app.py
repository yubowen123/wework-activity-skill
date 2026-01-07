"""
FastAPI主应用 - 简化启动版
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from .database import engine
from .models import Base
from .api import chats, rules, whitelist, rpa

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="企业微信活跃度管理系统",
    description="基于RPA的企业微信群聊活跃度分析与自动化管理",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(chats.router, prefix="/api/chats", tags=["群聊管理"])
app.include_router(rules.router, prefix="/api/rules", tags=["规则管理"])
app.include_router(whitelist.router, prefix="/api/whitelist", tags=["白名单"])
app.include_router(rpa.router, prefix="/api/rpa", tags=["RPA控制"])


@app.get("/")
def root():
    """首页"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>企业微信活跃度管理系统</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #409EFF; }
            .links { margin-top: 30px; }
            .links a {
                display: inline-block;
                margin: 10px 10px 10px 0;
                padding: 10px 20px;
                background: #409EFF;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            .links a:hover { background: #66b1ff; }
            .status {
                background: #67C23A;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 企业微信活跃度管理系统</h1>
            <p><span class="status">✓ 后端服务运行中</span></p>

            <h2>📚 快速链接</h2>
            <div class="links">
                <a href="/docs" target="_blank">📖 API文档 (Swagger)</a>
                <a href="/redoc" target="_blank">📘 API文档 (ReDoc)</a>
                <a href="/api/health">🏥 健康检查</a>
            </div>

            <h2>🚀 下一步</h2>
            <ol>
                <li>访问 <strong>http://localhost:5173</strong> 查看前端界面（需先启动前端）</li>
                <li>查看 <a href="/docs">API文档</a> 了解接口</li>
                <li>开始配置监控群聊</li>
            </ol>

            <h2>📋 系统状态</h2>
            <ul>
                <li>✅ 数据库已初始化</li>
                <li>✅ API服务正常</li>
                <li>⏳ 等待前端连接...</li>
            </ul>
        </div>
    </body>
    </html>
    """)


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "企业微信活跃度管理系统运行正常",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 启动企业微信活跃度管理系统")
    print("=" * 50)
    print("📍 访问地址:")
    print("   主页: http://localhost:8000")
    print("   API文档: http://localhost:8000/docs")
    print("=" * 50)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
