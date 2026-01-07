#!/usr/bin/env python3
"""
企业微信活跃度管理系统 - GUI 桌面应用
集成 Web 界面、后端 API 和 RPA 自动化
"""

import sys
import time
import threading
import logging
import webbrowser
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import webview
from web.app import app as fastapi_app
from rpa.scheduler import create_default_scheduler
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeWorkApp:
    """企业微信活跃度管理桌面应用"""

    def __init__(self):
        self.backend_port = 8000
        self.frontend_port = 5173
        self.backend_thread = None
        self.rpa_scheduler = None
        self.window = None

    def start_backend(self):
        """启动 FastAPI 后端"""
        try:
            logger.info("启动后端服务...")
            config = uvicorn.Config(
                fastapi_app,
                host="127.0.0.1",
                port=self.backend_port,
                log_level="info",
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

    def expose_api(self):
        """暴露给前端的 JavaScript API"""

        class Api:
            def __init__(self, app):
                self.app = app

            def open_docs(self):
                """打开 API 文档"""
                webbrowser.open(f"http://localhost:{self.app.backend_port}/docs")

            def restart_rpa(self):
                """重启 RPA 调度器"""
                self.app.stop_rpa_scheduler()
                time.sleep(1)
                threading.Thread(target=self.app.start_rpa_scheduler, daemon=True).start()
                return {"status": "success", "message": "RPA 调度器重启中..."}

            def get_app_info(self):
                """获取应用信息"""
                return {
                    "name": "企业微信活跃度管理系统",
                    "version": "1.0.0",
                    "backend_url": f"http://localhost:{self.app.backend_port}",
                    "rpa_running": self.app.rpa_scheduler is not None
                }

        return Api(self)

    def on_closed(self):
        """窗口关闭事件"""
        logger.info("应用正在关闭...")
        self.stop_rpa_scheduler()
        # 给一点时间让线程清理
        time.sleep(1)
        logger.info("✅ 应用已关闭")

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
            background_color='#F5F5F5',
            js_api=self.expose_api()
        )

        # 设置关闭事件
        self.window.events.closed += self.on_closed

        logger.info("✅ 应用窗口已创建")
        logger.info("=" * 50)

        # 启动 WebView（这会阻塞直到窗口关闭）
        webview.start(debug=False)


def main():
    """主函数"""
    try:
        app = WeWorkApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("\n用户中断")
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
    finally:
        logger.info("应用已退出")


if __name__ == "__main__":
    main()
