#!/bin/bash

# 企业微信 RPA 启动脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "  企业微信活跃度管理 - RPA 自动化"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查后端服务
echo "📍 检查后端服务..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务未运行，请先启动后端"
    echo "   运行: python -m web.app"
    exit 1
fi

echo ""
echo "🤖 启动 RPA 调度器..."
echo ""

# 启动 RPA
python -m rpa.main scheduler

echo ""
echo "✅ RPA 已停止"
