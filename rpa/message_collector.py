"""
消息采集器模块
从企业微信收集群聊消息并存储到数据库
"""

import re
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from .wework_automation import WeWorkAutomation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageCollector:
    """消息采集器"""

    def __init__(self, api_base_url: str = "http://localhost:8000", debug: bool = False):
        """
        初始化消息采集器

        Args:
            api_base_url: 后端 API 地址
            debug: 是否开启调试模式
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.automation = WeWorkAutomation(debug=debug)
        self.debug = debug

    def get_monitored_chats(self) -> List[Dict]:
        """
        从后端获取需要监控的群聊列表

        Returns:
            群聊列表
        """
        try:
            response = requests.get(f"{self.api_base_url}/api/chats")
            response.raise_for_status()
            chats = response.json()

            # 过滤出启用监控的群聊
            enabled_chats = [chat for chat in chats if chat.get('enabled', False)]

            logger.info(f"获取到 {len(enabled_chats)} 个需要监控的群聊")
            return enabled_chats

        except Exception as e:
            logger.error(f"获取监控群聊列表失败: {e}")
            return []

    def parse_message_text(self, text: str) -> Optional[Dict]:
        """
        解析消息文本，提取发送者、时间、内容

        企业微信消息格式示例：
        张三 10:30
        这是消息内容

        或者：
        李四 昨天 15:45
        消息内容

        Args:
            text: 消息文本

        Returns:
            解析后的消息字典
        """
        try:
            lines = text.strip().split('\n')
            if len(lines) < 2:
                return None

            # 第一行：发送者和时间
            header = lines[0]

            # 尝试匹配不同的时间格式
            # 格式1: "张三 10:30"
            pattern1 = r'^(.+?)\s+(\d{1,2}:\d{2})$'
            # 格式2: "张三 昨天 10:30"
            pattern2 = r'^(.+?)\s+(昨天|今天|前天)\s+(\d{1,2}:\d{2})$'
            # 格式3: "张三 2024/01/07 10:30"
            pattern3 = r'^(.+?)\s+(\d{4}/\d{1,2}/\d{1,2})\s+(\d{1,2}:\d{2})$'

            sender = None
            message_time = None

            # 尝试匹配格式1
            match = re.match(pattern1, header)
            if match:
                sender = match.group(1).strip()
                time_str = match.group(2)
                # 假设是今天
                today = datetime.now().strftime('%Y-%m-%d')
                message_time = datetime.strptime(f"{today} {time_str}", '%Y-%m-%d %H:%M')

            # 尝试匹配格式2
            if not match:
                match = re.match(pattern2, header)
                if match:
                    sender = match.group(1).strip()
                    day_ref = match.group(2)
                    time_str = match.group(3)

                    # 计算日期
                    from datetime import timedelta
                    now = datetime.now()
                    if day_ref == '今天':
                        date = now
                    elif day_ref == '昨天':
                        date = now - timedelta(days=1)
                    elif day_ref == '前天':
                        date = now - timedelta(days=2)
                    else:
                        date = now

                    date_str = date.strftime('%Y-%m-%d')
                    message_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')

            # 尝试匹配格式3
            if not match:
                match = re.match(pattern3, header)
                if match:
                    sender = match.group(1).strip()
                    date_str = match.group(2).replace('/', '-')
                    time_str = match.group(3)
                    message_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')

            if not sender or not message_time:
                logger.debug(f"无法解析消息头: {header}")
                return None

            # 消息内容（第二行及之后）
            content = '\n'.join(lines[1:]).strip()

            return {
                'sender': sender,
                'sent_at': message_time.isoformat(),
                'content': content
            }

        except Exception as e:
            logger.debug(f"解析消息失败: {e}, 文本: {text}")
            return None

    def collect_messages_from_chat(self, chat_name: str, limit: int = 100) -> List[Dict]:
        """
        从指定群聊收集消息

        Args:
            chat_name: 群聊名称
            limit: 最多收集的消息数量

        Returns:
            消息列表
        """
        messages = []

        try:
            # 确保企业微信正在运行
            if not self.automation.is_running():
                if not self.automation.launch_app():
                    logger.error("无法启动企业微信")
                    return messages

            # 搜索并打开群聊
            if not self.automation.search_chat(chat_name):
                logger.error(f"无法打开群聊: {chat_name}")
                return messages

            logger.info(f"开始采集群聊 '{chat_name}' 的消息...")

            # TODO: 实际的消息采集逻辑
            # 这里需要根据企业微信的实际UI实现：
            # 1. 滚动到历史消息
            # 2. 逐条读取消息（可能需要OCR或复制文本）
            # 3. 解析消息内容

            # 示例：模拟采集（实际需要替换为真实实现）
            logger.warning("消息采集功能需要根据实际UI实现")

            # 临时方案：手动导出消息后，可以通过此方法解析
            # 或者使用屏幕OCR技术读取消息

        except Exception as e:
            logger.error(f"采集消息时出错: {e}")

        return messages

    def save_messages_to_db(self, chat_id: int, messages: List[Dict]) -> int:
        """
        将消息保存到数据库

        Args:
            chat_id: 群聊ID
            messages: 消息列表

        Returns:
            成功保存的消息数量
        """
        saved_count = 0

        try:
            for msg in messages:
                data = {
                    "chat_id": chat_id,
                    "sender": msg['sender'],
                    "content": msg.get('content', ''),
                    "sent_at": msg['sent_at']
                }

                response = requests.post(
                    f"{self.api_base_url}/api/messages",
                    json=data
                )

                if response.status_code == 201:
                    saved_count += 1
                else:
                    logger.warning(f"保存消息失败: {response.text}")

            logger.info(f"成功保存 {saved_count}/{len(messages)} 条消息")

        except Exception as e:
            logger.error(f"保存消息到数据库失败: {e}")

        return saved_count

    def collect_all(self) -> Dict[str, int]:
        """
        采集所有监控群聊的消息

        Returns:
            采集统计 {chat_name: message_count}
        """
        stats = {}

        # 获取需要监控的群聊
        chats = self.get_monitored_chats()

        if not chats:
            logger.warning("没有需要监控的群聊")
            return stats

        # 逐个群聊采集
        for chat in chats:
            chat_id = chat['id']
            chat_name = chat['chat_name']

            logger.info(f"开始采集群聊: {chat_name}")

            # 采集消息
            messages = self.collect_messages_from_chat(chat_name)

            # 保存到数据库
            if messages:
                saved_count = self.save_messages_to_db(chat_id, messages)
                stats[chat_name] = saved_count
            else:
                stats[chat_name] = 0

        return stats

    def import_from_text_file(self, chat_name: str, file_path: str) -> int:
        """
        从文本文件导入消息（手动导出的聊天记录）

        Args:
            chat_name: 群聊名称
            file_path: 文本文件路径

        Returns:
            导入的消息数量
        """
        try:
            # 获取群聊ID
            response = requests.get(f"{self.api_base_url}/api/chats")
            response.raise_for_status()
            chats = response.json()

            chat = next((c for c in chats if c['chat_name'] == chat_name), None)
            if not chat:
                logger.error(f"未找到群聊: {chat_name}")
                return 0

            chat_id = chat['id']

            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 按消息分割（假设消息之间有空行）
            message_blocks = content.split('\n\n')

            messages = []
            for block in message_blocks:
                parsed = self.parse_message_text(block)
                if parsed:
                    messages.append(parsed)

            # 保存到数据库
            saved_count = self.save_messages_to_db(chat_id, messages)

            logger.info(f"从文件导入 {saved_count} 条消息")
            return saved_count

        except Exception as e:
            logger.error(f"从文件导入消息失败: {e}")
            return 0


# 测试代码
if __name__ == "__main__":
    collector = MessageCollector(debug=True)

    # 测试解析消息
    test_message = """张三 10:30
这是一条测试消息"""

    parsed = collector.parse_message_text(test_message)
    print(f"解析结果: {parsed}")

    # 测试获取监控群聊
    chats = collector.get_monitored_chats()
    print(f"监控群聊: {chats}")
