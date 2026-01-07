#!/bin/bash

# 创建 macOS DMG 安装包

cd "$(dirname "$0")"

APP_NAME="WeWorkActivity"
DMG_NAME="企业微信活跃度管理-v1.0.0"
VOLUME_NAME="企业微信活跃度管理"

echo "=========================================="
echo "  创建 DMG 安装包"
echo "=========================================="
echo ""

# 检查应用是否存在
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ 应用不存在: dist/${APP_NAME}.app"
    echo "请先运行: ./build_app.sh"
    exit 1
fi

# 创建临时目录
echo "📍 准备文件..."
TMP_DIR=$(mktemp -d)
mkdir -p "$TMP_DIR"

# 复制应用到临时目录
cp -R "dist/${APP_NAME}.app" "$TMP_DIR/"

# 创建应用程序文件夹快捷方式
ln -s /Applications "$TMP_DIR/Applications"

# 添加说明文件（可选）
cat > "$TMP_DIR/README.txt" << EOF
企业微信活跃度管理系统 v1.0.0

安装方法:
1. 将 ${APP_NAME}.app 拖动到 Applications 文件夹
2. 首次打开可能需要在「系统偏好设置 → 安全性与隐私」中允许运行
3. 双击应用图标启动

功能特性:
- Web 可视化管理界面
- 自动化 RPA 引擎
- 活跃度分析与规则执行
- 系统托盘后台运行

需要帮助?
查看项目文档: APP_GUIDE.md
EOF

# 创建 DMG
echo "📍 创建 DMG 镜像..."
hdiutil create -volname "$VOLUME_NAME" \
    -srcfolder "$TMP_DIR" \
    -ov -format UDZO \
    "dist/${DMG_NAME}.dmg"

# 清理临时文件
rm -rf "$TMP_DIR"

# 检查结果
if [ -f "dist/${DMG_NAME}.dmg" ]; then
    echo ""
    echo "=========================================="
    echo "✅ DMG 创建成功！"
    echo "=========================================="
    echo ""
    echo "文件位置: dist/${DMG_NAME}.dmg"
    echo "文件大小:"
    ls -lh "dist/${DMG_NAME}.dmg"
    echo ""
    echo "🚀 使用方法:"
    echo "   双击 DMG 文件挂载"
    echo "   将应用拖动到 Applications 文件夹"
    echo ""
    echo "=========================================="
else
    echo ""
    echo "❌ DMG 创建失败"
    exit 1
fi
