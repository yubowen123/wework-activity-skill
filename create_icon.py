#!/usr/bin/env python3
"""
生成应用图标
创建 macOS .icns 和 Windows .ico 图标文件
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_app_icon(size=1024):
    """
    创建应用图标

    Args:
        size: 图标尺寸（正方形）

    Returns:
        PIL Image对象
    """
    # 创建画布
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 绘制渐变背景圆形
    # 主色调：#409EFF (Element Plus 蓝色)
    padding = size // 10

    # 画外圆（阴影效果）
    draw.ellipse(
        [padding + 10, padding + 10, size - padding + 10, size - padding + 10],
        fill=(64, 158, 255, 50)
    )

    # 画主圆
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=(64, 158, 255, 255),
        outline=(32, 79, 128, 255),
        width=size // 100
    )

    # 在中间绘制图标符号（简化的微信图标）
    # 绘制对话框图标
    center_x = size // 2
    center_y = size // 2

    # 大对话框
    bubble_size = size // 3
    bubble_x = center_x - bubble_size // 2
    bubble_y = center_y - bubble_size // 2

    draw.rounded_rectangle(
        [bubble_x, bubble_y, bubble_x + bubble_size, bubble_y + bubble_size],
        radius=size // 20,
        fill=(255, 255, 255, 255)
    )

    # 小对话框（右下角）
    small_bubble_size = bubble_size // 2
    small_x = center_x + bubble_size // 4
    small_y = center_y + bubble_size // 4

    draw.rounded_rectangle(
        [small_x, small_y, small_x + small_bubble_size, small_y + small_bubble_size],
        radius=size // 30,
        fill=(230, 244, 255, 255)
    )

    # 在大对话框中绘制简单的线条（表示文字）
    line_y = bubble_y + bubble_size // 3
    line_spacing = bubble_size // 6
    line_padding = bubble_size // 5

    for i in range(3):
        y = line_y + i * line_spacing
        draw.line(
            [bubble_x + line_padding, y, bubble_x + bubble_size - line_padding, y],
            fill=(64, 158, 255, 255),
            width=size // 100
        )

    return image


def save_png_icons(base_image, output_dir):
    """
    保存多种尺寸的 PNG 图标

    Args:
        base_image: 基础图像
        output_dir: 输出目录
    """
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    for size in sizes:
        resized = base_image.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(output_dir / f"icon_{size}.png")
        print(f"✅ 已生成: icon_{size}.png")


def create_ico(base_image, output_path):
    """
    创建 Windows .ico 文件

    Args:
        base_image: 基础图像
        output_path: 输出路径
    """
    sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
    base_image.save(
        output_path,
        format='ICO',
        sizes=sizes
    )
    print(f"✅ 已生成: {output_path.name}")


def create_icns(png_dir, output_path):
    """
    创建 macOS .icns 文件
    需要使用 iconutil 命令

    Args:
        png_dir: PNG 图标目录
        output_path: 输出路径
    """
    import subprocess
    import tempfile
    import shutil

    # 创建临时 iconset 目录
    with tempfile.TemporaryDirectory() as temp_dir:
        iconset_dir = Path(temp_dir) / "AppIcon.iconset"
        iconset_dir.mkdir()

        # 复制并重命名 PNG 文件为 macOS 要求的格式
        icon_mappings = {
            16: "icon_16x16.png",
            32: ["icon_16x16@2x.png", "icon_32x32.png"],
            64: "icon_32x32@2x.png",
            128: "icon_128x128.png",
            256: ["icon_128x128@2x.png", "icon_256x256.png"],
            512: ["icon_256x256@2x.png", "icon_512x512.png"],
            1024: "icon_512x512@2x.png"
        }

        for size, names in icon_mappings.items():
            source = png_dir / f"icon_{size}.png"
            if not source.exists():
                continue

            if isinstance(names, str):
                names = [names]

            for name in names:
                shutil.copy(source, iconset_dir / name)

        # 使用 iconutil 生成 .icns
        try:
            subprocess.run(
                ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)],
                check=True,
                capture_output=True
            )
            print(f"✅ 已生成: {output_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 生成 .icns 失败: {e.stderr.decode()}")
        except FileNotFoundError:
            print("❌ iconutil 命令未找到（需要 macOS 系统）")


def main():
    """主函数"""
    print("=" * 50)
    print("生成应用图标")
    print("=" * 50)

    # 输出目录
    output_dir = Path(__file__).parent / "resources"
    output_dir.mkdir(exist_ok=True)

    # 生成基础图标
    print("\n生成基础图标 (1024x1024)...")
    base_icon = create_app_icon(1024)

    # 保存 PNG 图标
    print("\n生成 PNG 图标...")
    save_png_icons(base_icon, output_dir)

    # 生成 .ico（Windows）
    print("\n生成 Windows 图标...")
    create_ico(base_icon, output_dir / "icon.ico")

    # 生成 .icns（macOS）
    print("\n生成 macOS 图标...")
    create_icns(output_dir, output_dir / "icon.icns")

    print("\n" + "=" * 50)
    print("✅ 图标生成完成！")
    print(f"输出目录: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
