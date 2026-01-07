"""
企业微信自动化核心模块
使用 pyautogui 和 macOS API 控制企业微信客户端
"""

import time
import pyautogui
import pyperclip
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

try:
    from AppKit import NSWorkspace, NSRunningApplication
except ImportError:
    logging.warning("AppKit not available. Some macOS-specific features may not work.")

# 配置 pyautogui
pyautogui.FAILSAFE = True  # 鼠标移到屏幕角落停止
pyautogui.PAUSE = 0.5  # 每次操作后暂停0.5秒

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeWorkAutomation:
    """企业微信自动化控制类"""

    def __init__(self, debug: bool = False):
        """
        初始化企业微信自动化

        Args:
            debug: 是否开启调试模式（会保存截图）
        """
        self.debug = debug
        self.app_name = "企业微信"
        self.bundle_id = "com.tencent.WeWorkMac"

        # 截图保存路径
        if debug:
            self.screenshot_dir = Path(__file__).parent.parent / "debug_screenshots"
            self.screenshot_dir.mkdir(exist_ok=True)

    def is_running(self) -> bool:
        """检查企业微信是否正在运行"""
        try:
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()

            for app in running_apps:
                if app.bundleIdentifier() == self.bundle_id:
                    return True
            return False
        except Exception as e:
            logger.warning(f"无法检查应用状态: {e}")
            # 降级方案：使用 osascript
            import subprocess
            try:
                result = subprocess.run(
                    ['osascript', '-e', f'tell application "System Events" to (name of processes) contains "{self.app_name}"'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.stdout.strip() == "true"
            except Exception as e2:
                logger.error(f"降级检查也失败: {e2}")
                return False

    def launch_app(self, wait_time: int = 5) -> bool:
        """
        启动企业微信

        Args:
            wait_time: 等待应用启动的时间（秒）

        Returns:
            是否成功启动
        """
        try:
            if self.is_running():
                logger.info("企业微信已在运行")
                return True

            logger.info("正在启动企业微信...")
            workspace = NSWorkspace.sharedWorkspace()
            success = workspace.launchApplication_(self.app_name)

            if not success:
                logger.error("启动失败")
                return False

            # 等待应用完全启动
            time.sleep(wait_time)

            # 验证是否启动成功
            if self.is_running():
                logger.info("企业微信启动成功")
                return True
            else:
                logger.error("企业微信未能成功启动")
                return False

        except Exception as e:
            logger.error(f"启动企业微信时出错: {e}")
            return False

    def activate_app(self) -> bool:
        """激活企业微信窗口（置于前台）"""
        try:
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()

            for app in running_apps:
                if app.bundleIdentifier() == self.bundle_id:
                    app.activateWithOptions_(1)  # NSApplicationActivateIgnoringOtherApps
                    time.sleep(0.5)
                    logger.info("企业微信已激活")
                    return True

            logger.warning("未找到运行中的企业微信")
            return False
        except Exception as e:
            logger.error(f"激活企业微信时出错: {e}")
            return False

    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        在屏幕上查找图像

        Args:
            image_path: 图像文件路径
            confidence: 匹配置信度 (0-1)

        Returns:
            图像中心坐标 (x, y)，未找到则返回 None
        """
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                logger.info(f"找到图像 {image_path} 于 {location}")
            return location
        except Exception as e:
            logger.debug(f"未找到图像 {image_path}: {e}")
            return None

    def click_at(self, x: int, y: int, clicks: int = 1, interval: float = 0.5):
        """
        在指定坐标点击

        Args:
            x: X 坐标
            y: Y 坐标
            clicks: 点击次数
            interval: 点击间隔（秒）
        """
        pyautogui.click(x, y, clicks=clicks, interval=interval)
        logger.debug(f"点击坐标 ({x}, {y})")

    def click_image(self, image_path: str, confidence: float = 0.8, timeout: int = 10) -> bool:
        """
        查找并点击图像

        Args:
            image_path: 图像文件路径
            confidence: 匹配置信度
            timeout: 超时时间（秒）

        Returns:
            是否成功点击
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            location = self.find_on_screen(image_path, confidence)
            if location:
                self.click_at(location[0], location[1])
                return True
            time.sleep(0.5)

        logger.warning(f"超时未找到图像: {image_path}")
        return False

    def search_chat(self, chat_name: str) -> bool:
        """
        搜索并打开指定群聊

        Args:
            chat_name: 群聊名称

        Returns:
            是否成功打开
        """
        try:
            # 激活企业微信
            if not self.activate_app():
                return False

            # 使用快捷键打开搜索框 (Cmd+F)
            pyautogui.hotkey('command', 'f')
            time.sleep(0.5)

            # 清空搜索框并输入群聊名称
            pyautogui.hotkey('command', 'a')
            time.sleep(0.2)

            # 使用剪贴板输入（支持中文）
            pyperclip.copy(chat_name)
            pyautogui.hotkey('command', 'v')
            time.sleep(1)

            # 按回车打开第一个搜索结果
            pyautogui.press('enter')
            time.sleep(1)

            logger.info(f"已打开群聊: {chat_name}")
            return True

        except Exception as e:
            logger.error(f"搜索群聊失败: {e}")
            return False

    def scroll_up(self, clicks: int = 5):
        """
        向上滚动消息列表

        Args:
            clicks: 滚动次数
        """
        pyautogui.scroll(clicks)
        time.sleep(0.3)

    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """
        截取当前屏幕

        Args:
            filename: 保存文件名（不含扩展名）

        Returns:
            截图文件路径
        """
        if not self.debug:
            return None

        try:
            if filename is None:
                filename = f"screenshot_{int(time.time())}"

            filepath = self.screenshot_dir / f"{filename}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)

            logger.info(f"截图已保存: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    def get_clipboard_content(self) -> str:
        """获取剪贴板内容"""
        return pyperclip.paste()

    def copy_selected_text(self) -> str:
        """
        复制当前选中的文本

        Returns:
            复制的文本内容
        """
        # 清空剪贴板
        pyperclip.copy("")

        # 复制选中内容
        pyautogui.hotkey('command', 'c')
        time.sleep(0.2)

        # 获取剪贴板内容
        return self.get_clipboard_content()

    def select_message(self, message_index: int = 0):
        """
        选择消息（用于复制）

        Args:
            message_index: 消息索引（从上往下）
        """
        # 这个方法需要根据实际UI调整
        # 可能需要通过坐标点击特定消息
        pass

    def right_click_member(self, member_name: str) -> bool:
        """
        右键点击群成员

        Args:
            member_name: 成员名称

        Returns:
            是否成功
        """
        try:
            # 这需要根据实际UI实现
            # 通常需要：
            # 1. 点击群聊信息按钮
            # 2. 找到成员列表
            # 3. 搜索并右键点击成员
            logger.warning("right_click_member 需要根据实际UI实现")
            return False
        except Exception as e:
            logger.error(f"右键点击成员失败: {e}")
            return False

    def remove_member(self, member_name: str) -> bool:
        """
        从群聊中移除成员

        Args:
            member_name: 成员名称

        Returns:
            是否成功移除
        """
        try:
            # 1. 点击群聊详情按钮
            # 2. 找到成员
            # 3. 点击移除
            # 4. 确认

            logger.warning("remove_member 需要根据实际UI实现")
            logger.info(f"模拟移除成员: {member_name}")

            # 这里需要根据企业微信实际UI来实现
            # 可能的步骤：
            # - 打开群详情
            # - 滚动找到成员
            # - 右键菜单选择"移出群聊"
            # - 确认对话框

            return False
        except Exception as e:
            logger.error(f"移除成员失败: {e}")
            return False

    def get_chat_info(self) -> Dict:
        """
        获取当前群聊信息

        Returns:
            群聊信息字典
        """
        try:
            # 点击群聊详情
            # 读取群名称、成员数等信息

            return {
                "chat_name": "待实现",
                "member_count": 0,
                "members": []
            }
        except Exception as e:
            logger.error(f"获取群聊信息失败: {e}")
            return {}

    def close_app(self):
        """关闭企业微信"""
        try:
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()

            for app in running_apps:
                if app.bundleIdentifier() == self.bundle_id:
                    app.terminate()
                    logger.info("企业微信已关闭")
                    return True

            return False
        except Exception as e:
            logger.error(f"关闭企业微信失败: {e}")
            return False


# 测试代码
if __name__ == "__main__":
    # 创建自动化实例
    automation = WeWorkAutomation(debug=True)

    # 测试启动
    if automation.launch_app():
        print("✅ 企业微信已启动")

        # 测试搜索群聊
        # automation.search_chat("测试群")

        # 测试截图
        automation.take_screenshot("test")

        print("✅ 测试完成")
    else:
        print("❌ 启动失败")
