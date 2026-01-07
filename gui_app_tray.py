#!/usr/bin/env python3
"""
企业微信活跃度管理系统 - 带系统托盘的 GUI 应用
"""

import sys
import time
import threading
import logging
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent))

import webview
from web.app import app as fastapi_app
from rpa.scheduler import create_default_scheduler
import uvicorn
from PIL import Image, ImageDraw
import pystray

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_icon():
    """创建系统托盘图标"""
    # 创建一个简单的图标（64x64，蓝色圆形）
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # 画一个蓝色圆形
    draw.ellipse([8, 8, 56, 56], fill='#409EFF', outline='#409EFF')

    # 在中间画字母 W（代表 WeWork）
    # 这里用简单的矩形模拟，实际可以用字体
    draw.text((20, 18), 'W', fill='white')

    return image


class WeWorkAppWithTray:
    """带系统托盘的企业微信活跃度管理桌面应用"""

    def __init__(self):
        self.backend_port = 8000
        self.frontend_port = 5173
        self.backend_thread = None
        self.rpa_scheduler = None
        self.window = None
        self.tray_icon = None
        self.is_running = True

    def start_backend(self):
        """启动 FastAPI 后端"""
        try:
            logger.info("启动后端服务...")
            config = uvicorn.Config(
                fastapi_app,
                host="127.0.0.1",
                port=self.backend_port,
                log_level="warning",
                access_log=False
            )
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            logger.error(f"后端启动失败: {e}")

    def start_rpa_scheduler(self):
        """启动 RPA 调度器"""
        try:
            logger.info("启动 RPA 调度器...")
            self.rpa_scheduler = create_default_scheduler(
                api_base_url=f"http://127.0.0.1:{self.backend_port}",
                debug=False
            )
            self.rpa_scheduler.start()
            logger.info("✅ RPA 调度器已启动")
        except Exception as e:
            logger.error(f"RPA 调度器启动失败: {e}")

    def stop_rpa_scheduler(self):
        """停止 RPA 调度器"""
        if self.rpa_scheduler:
            try:
                self.rpa_scheduler.stop()
                logger.info("RPA 调度器已停止")
            except Exception as e:
                logger.error(f"停止 RPA 调度器失败: {e}")

    def show_window(self, icon=None, item=None):
        """显示主窗口"""
        if self.window:
            try:
                self.window.show()
            except Exception as e:
                logger.error(f"显示窗口失败: {e}")

    def hide_window(self):
        """隐藏主窗口"""
        if self.window:
            try:
                self.window.hide()
            except Exception as e:
                logger.error(f"隐藏窗口失败: {e}")

    def quit_app(self, icon=None, item=None):
        """退出应用"""
        logger.info("退出应用...")
        self.is_running = False

        # 停止 RPA
        self.stop_rpa_scheduler()

        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()

        # 销毁窗口
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass

        logger.info("✅ 应用已退出")

    def create_tray_menu(self):
        """创建托盘菜单"""
        menu = pystray.Menu(
            pystray.MenuItem("显示主界面", self.show_window, default=True),
            pystray.MenuItem("重启 RPA", self.restart_rpa),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self.quit_app)
        )
        return menu

    def restart_rpa(self, icon=None, item=None):
        """重启 RPA 调度器"""
        logger.info("重启 RPA 调度器...")
        self.stop_rpa_scheduler()
        time.sleep(1)
        threading.Thread(target=self.start_rpa_scheduler, daemon=True).start()

    def setup_tray_icon(self):
        """设置系统托盘图标"""
        try:
            icon_image = create_icon()
            self.tray_icon = pystray.Icon(
                "wework_activity",
                icon_image,
                "企业微信活跃度管理",
                menu=self.create_tray_menu()
            )

            # 在后台线程运行托盘图标
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            logger.info("✅ 系统托盘图标已创建")
        except Exception as e:
            logger.error(f"创建托盘图标失败: {e}")

    def on_closed(self):
        """窗口关闭事件 - 最小化到托盘而不是退出"""
        logger.info("窗口关闭，最小化到托盘")
        # 不做任何事，让窗口最小化到托盘
        # 实际退出需要从托盘菜单选择"退出"

    def run(self):
        """运行应用"""
        logger.info("=" * 50)
        logger.info("启动企业微信活跃度管理系统")
        logger.info("=" * 50)

        # 启动后端（在后台线程）
        self.backend_thread = threading.Thread(target=self.start_backend, daemon=True)
        self.backend_thread.start()

        # 等待后端启动
        logger.info("等待后端服务启动...")
        time.sleep(3)

        # 启动 RPA 调度器（在后台线程）
        rpa_thread = threading.Thread(target=self.start_rpa_scheduler, daemon=True)
        rpa_thread.start()

        # 设置系统托盘图标
        self.setup_tray_icon()

        # 创建 WebView 窗口
        logger.info("创建应用窗口...")

        # 检查前端是否在运行
        frontend_url = f"http://localhost:{self.frontend_port}"

        try:
            import requests
            response = requests.get(frontend_url, timeout=2)
            if response.status_code == 200:
                logger.info(f"✅ 检测到前端服务运行在 {frontend_url}")
                url = frontend_url
            else:
                raise Exception("前端未运行")
        except Exception:
            logger.warning("⚠️  前端开发服务器未运行，将使用后端首页")
            url = f"http://localhost:{self.backend_port}"

        # 创建窗口
        self.window = webview.create_window(
            title="企业微信活跃度管理系统",
            url=url,
            width=1400,
            height=900,
            resizable=True,
            fullscreen=False,
            min_size=(1200, 800),
            background_color='#F5F5F5'
        )

        # 设置关闭事件
        self.window.events.closed += self.on_closed

        logger.info("✅ 应用窗口已创建")
        logger.info("💡 提示：关闭窗口后应用会最小化到系统托盘")
        logger.info("=" * 50)

        # 启动 WebView（这会阻塞直到窗口关闭）
        webview.start(debug=False)


def main():
    """主函数"""
    try:
        app = WeWorkAppWithTray()
        app.run()
    except KeyboardInterrupt:
        logger.info("\n用户中断")
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
    finally:
        logger.info("应用已退出")


if __name__ == "__main__":
    main()
