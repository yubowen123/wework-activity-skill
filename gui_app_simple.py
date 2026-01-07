#!/usr/bin/env python3
"""
企业微信活跃度管理系统 - 简化版桌面应用
使用默认浏览器打开，避免 webview 沙盒问题
"""

import sys
import time
import threading
import logging
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from web.app import app as fastapi_app
from rpa.scheduler import create_default_scheduler
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeWorkBrowserApp:
    """企业微信活跃度管理系统 - 浏览器版"""

    def __init__(self):
        self.backend_port = 8000
        self.frontend_port = 5173
        self.backend_thread = None
        self.rpa_scheduler = None

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

            # 注入到 API 中，让 Web 界面可以控制
            from web.api import rpa as rpa_api
            rpa_api.set_rpa_scheduler(self.rpa_scheduler)

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

    def open_browser(self):
        """在浏览器中打开应用"""
        # 检查前端是否在运行
        frontend_url = f"http://localhost:{self.frontend_port}"

        try:
            import requests
            response = requests.get(frontend_url, timeout=2)
            if response.status_code == 200:
                logger.info(f"✅ 检测到前端服务，打开: {frontend_url}")
                url = frontend_url
            else:
                raise Exception("前端未运行")
        except Exception:
            logger.warning("⚠️  前端未运行，使用后端页面")
            url = f"http://localhost:{self.backend_port}"

        # 打开浏览器
        logger.info(f"在默认浏览器中打开: {url}")
        webbrowser.open(url)

    def run(self):
        """运行应用"""
        logger.info("=" * 60)
        logger.info("企业微信活跃度管理系统 - 浏览器版")
        logger.info("=" * 60)

        # 启动后端（在后台线程）
        self.backend_thread = threading.Thread(target=self.start_backend, daemon=True)
        self.backend_thread.start()

        # 等待后端启动
        logger.info("等待后端服务启动...")
        time.sleep(3)

        # 启动 RPA 调度器
        rpa_thread = threading.Thread(target=self.start_rpa_scheduler, daemon=True)
        rpa_thread.start()
        time.sleep(2)

        # 在浏览器中打开
        self.open_browser()

        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ 应用已在浏览器中打开")
        logger.info("")
        logger.info("服务地址:")
        logger.info(f"  - 后端 API: http://localhost:{self.backend_port}")
        logger.info(f"  - 前端界面: http://localhost:{self.frontend_port}")
        logger.info(f"  - API 文档: http://localhost:{self.backend_port}/docs")
        logger.info("")
        logger.info("💡 提示:")
        logger.info("  - 按 Ctrl+C 停止服务")
        logger.info("  - RPA 调度器已在后台运行")
        logger.info("  - 关闭终端会停止所有服务")
        logger.info("=" * 60)

        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n正在停止服务...")
            self.stop_rpa_scheduler()
            logger.info("✅ 应用已停止")


def main():
    """主函数"""
    try:
        app = WeWorkBrowserApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("\n用户中断")
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
    finally:
        logger.info("应用已退出")


if __name__ == "__main__":
    main()
