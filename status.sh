#!/bin/bash

echo "==========================================="
echo "   企业微信活跃度管理系统 - 状态检查"
echo "==========================================="
echo ""

# 检查后端
echo "📍 检查后端服务..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务正常 (http://localhost:8000)"
    curl -s http://localhost:8000/api/health | python3 -m json.tool
else
    echo "❌ 后端服务未运行"
fi

echo ""

# 检查前端
echo "📍 检查前端服务..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ | grep -q "200"; then
    echo "✅ 前端服务正常 (http://localhost:5173)"
else
    echo "❌ 前端服务未运行"
fi

echo ""

# 检查数据库
echo "📍 检查数据库..."
DB_PATH="/Users/gb/wework-activity-skill/data/wework.db"
if [ -f "$DB_PATH" ]; then
    echo "✅ 数据库文件存在"
    ls -lh "$DB_PATH"
else
    echo "❌ 数据库文件不存在"
fi

echo ""

# 检查进程
echo "📍 运行中的进程:"
echo "后端进程:"
ps aux | grep "web.app" | grep -v grep || echo "  未找到"
echo ""
echo "前端进程:"
ps aux | grep "vite" | grep -v grep | head -1 || echo "  未找到"

echo ""
echo "==========================================="
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8000"
echo "  文档: http://localhost:8000/docs"
echo "==========================================="
