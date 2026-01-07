#!/bin/bash

echo "========================================"
echo "  企业微信活跃度管理系统 - 启动脚本"
echo "========================================"

cd "$(dirname "$0")"

# 检查后端是否运行
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ 后端服务已在运行 (端口8000)"
else
    echo "🚀 启动后端服务..."
    python3 -m web.app > backend.log 2>&1 &
    echo "   后端PID: $!"
    sleep 2
fi

# 检查前端是否运行
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ 前端服务已在运行 (端口5173)"
else
    echo "🚀 启动前端服务..."
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    echo "   前端PID: $!"
    cd ..
    sleep 3
fi

echo ""
echo "========================================"
echo "✅ 服务已启动！"
echo ""
echo "📍 访问地址:"
echo "   前端界面: http://localhost:5173"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "🛑 停止服务:"
echo "   ./stop.sh"
echo "========================================"
