#!/bin/bash

# 企业微信活跃度管理系统 - 桌面应用启动脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "  企业微信活跃度管理系统 - 桌面应用"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📍 检查依赖..."
if ! python -c "import webview" 2>/dev/null; then
    echo "❌ GUI 依赖未安装"
    echo "正在安装..."
    pip install -r requirements.txt
fi

# 启动前端（可选）
if [ -d "frontend" ]; then
    echo ""
    echo "📍 检查前端服务..."
    if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "⚠️  前端开发服务器未运行"
        echo "提示：启动前端可获得更好的体验"
        echo "运行: cd frontend && npm run dev"
        echo ""
        echo "按任意键继续（使用后端默认页面）..."
        read -n 1 -s
    else
        echo "✅ 前端服务运行中"
    fi
fi

echo ""
echo "🚀 启动桌面应用..."
echo "💡 关闭窗口后应用会最小化到系统托盘"
echo ""

# 运行应用
python gui_app_tray.py

echo ""
echo "✅ 应用已退出"
