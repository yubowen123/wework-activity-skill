#!/bin/bash

# 企业微信活跃度管理系统 - 应用打包脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "  企业微信活跃度管理系统 - 应用打包"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 PyInstaller
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "❌ PyInstaller 未安装"
    echo "正在安装..."
    pip install pyinstaller
fi

# 清理旧的构建文件
echo "📍 清理旧的构建文件..."
rm -rf build/
rm -rf dist/
rm -rf __pycache__/

# 构建前端（如果需要）
echo ""
echo "📍 检查前端构建..."
if [ -d "frontend" ]; then
    if [ ! -d "frontend/dist" ]; then
        echo "⚠️  前端未构建，正在构建..."
        cd frontend
        npm run build
        cd ..
        echo "✅ 前端构建完成"
    else
        echo "✅ 前端已构建"
    fi
else
    echo "⚠️  前端目录不存在，将使用后端默认页面"
fi

# 生成图标（如果需要）
echo ""
echo "📍 检查应用图标..."
if [ ! -f "resources/icon.icns" ]; then
    echo "正在生成图标..."
    python create_icon.py
fi

# 打包应用
echo ""
echo "📍 开始打包应用..."
echo ""

pyinstaller wework_activity.spec --clean --noconfirm

# 检查打包结果
if [ -d "dist/WeWorkActivity.app" ]; then
    echo ""
    echo "=========================================="
    echo "✅ 打包成功！"
    echo "=========================================="
    echo ""
    echo "应用位置: dist/WeWorkActivity.app"
    echo ""
    echo "📦 应用信息:"
    ls -lh dist/WeWorkActivity.app/Contents/MacOS/WeWorkActivity
    echo ""
    echo "🚀 运行应用:"
    echo "   open dist/WeWorkActivity.app"
    echo ""
    echo "📦 创建 DMG 安装包:"
    echo "   ./create_dmg.sh"
    echo ""
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ 打包失败"
    echo "=========================================="
    echo ""
    echo "请检查上方的错误信息"
    exit 1
fi
