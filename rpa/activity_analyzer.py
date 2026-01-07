"""
活跃度分析器模块
分析用户在群聊中的活跃度
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActivityAnalyzer:
    """活跃度分析器"""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        初始化活跃度分析器

        Args:
            api_base_url: 后端 API 地址
        """
        self.api_base_url = api_base_url.rstrip('/')

    def get_chat_messages(self, chat_id: int, days: int = 30) -> List[Dict]:
        """
        获取指定群聊的消息

        Args:
            chat_id: 群聊ID
            days: 获取最近几天的消息

        Returns:
            消息列表
        """
        try:
            # 计算起始日期
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            response = requests.get(
                f"{self.api_base_url}/api/messages",
                params={
                    "chat_id": chat_id,
                    "start_date": start_date
                }
            )
            response.raise_for_status()

            messages = response.json()
            logger.info(f"获取到 {len(messages)} 条消息（最近 {days} 天）")
            return messages

        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []

    def calculate_daily_activity(self, messages: List[Dict]) -> Dict[str, Dict[str, int]]:
        """
        计算每个用户每天的活跃度（消息数）

        Args:
            messages: 消息列表

        Returns:
            {
                "user_name": {
                    "2024-01-01": 10,
                    "2024-01-02": 5,
                    ...
                }
            }
        """
        activity = defaultdict(lambda: defaultdict(int))

        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            sent_at = msg.get('sent_at', '')

            try:
                # 解析时间
                msg_time = datetime.fromisoformat(sent_at)
                date_key = msg_time.strftime('%Y-%m-%d')

                # 统计消息数
                activity[sender][date_key] += 1

            except Exception as e:
                logger.debug(f"解析消息时间失败: {e}")
                continue

        return dict(activity)

    def get_inactive_users(
        self,
        chat_id: int,
        inactive_days: int = 7,
        min_messages_per_day: int = 1
    ) -> List[Dict]:
        """
        获取不活跃的用户

        Args:
            chat_id: 群聊ID
            inactive_days: 连续不活跃天数阈值
            min_messages_per_day: 每天最少消息数（低于此数视为不活跃）

        Returns:
            不活跃用户列表，包含用户名和最后活跃时间
        """
        # 获取消息
        messages = self.get_chat_messages(chat_id, days=inactive_days + 7)

        if not messages:
            logger.warning(f"群聊 {chat_id} 没有消息数据")
            return []

        # 计算每日活跃度
        activity = self.calculate_daily_activity(messages)

        # 生成日期范围
        today = datetime.now().date()
        date_range = [
            (today - timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(inactive_days)
        ]

        inactive_users = []

        # 检查每个用户
        for user, user_activity in activity.items():
            # 检查最近 N 天的活跃度
            inactive_count = 0
            last_active_date = None

            for date_key in reversed(date_range):  # 从最近的日期开始
                msg_count = user_activity.get(date_key, 0)

                if msg_count < min_messages_per_day:
                    inactive_count += 1
                else:
                    # 找到活跃日期，记录并跳出
                    last_active_date = date_key
                    break

            # 如果连续不活跃天数达到阈值
            if inactive_count >= inactive_days:
                inactive_users.append({
                    'user_name': user,
                    'inactive_days': inactive_count,
                    'last_active_date': last_active_date or 'N/A'
                })

        logger.info(f"找到 {len(inactive_users)} 个不活跃用户（标准：连续 {inactive_days} 天少于 {min_messages_per_day} 条消息）")

        return inactive_users

    def get_user_statistics(self, chat_id: int, days: int = 30) -> List[Dict]:
        """
        获取用户统计信息

        Args:
            chat_id: 群聊ID
            days: 统计天数

        Returns:
            用户统计列表
        """
        messages = self.get_chat_messages(chat_id, days=days)

        if not messages:
            return []

        # 统计每个用户的消息数
        user_stats = defaultdict(lambda: {
            'total_messages': 0,
            'active_days': set()
        })

        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            sent_at = msg.get('sent_at', '')

            try:
                msg_time = datetime.fromisoformat(sent_at)
                date_key = msg_time.strftime('%Y-%m-%d')

                user_stats[sender]['total_messages'] += 1
                user_stats[sender]['active_days'].add(date_key)

            except Exception as e:
                logger.debug(f"解析消息时间失败: {e}")
                continue

        # 转换为列表格式
        result = []
        for user, stats in user_stats.items():
            result.append({
                'user_name': user,
                'total_messages': stats['total_messages'],
                'active_days_count': len(stats['active_days']),
                'avg_messages_per_day': round(stats['total_messages'] / days, 2)
            })

        # 按消息数降序排序
        result.sort(key=lambda x: x['total_messages'], reverse=True)

        return result

    def get_chat_statistics(self, chat_id: int, days: int = 30) -> Dict:
        """
        获取群聊统计信息

        Args:
            chat_id: 群聊ID
            days: 统计天数

        Returns:
            统计信息字典
        """
        messages = self.get_chat_messages(chat_id, days=days)

        if not messages:
            return {
                'total_messages': 0,
                'total_users': 0,
                'active_users': 0,
                'avg_messages_per_day': 0
            }

        # 统计
        total_messages = len(messages)
        unique_users = set(msg.get('sender', 'Unknown') for msg in messages)

        # 计算活跃用户（最近7天有发消息的）
        recent_date = datetime.now() - timedelta(days=7)
        active_users = set()

        for msg in messages:
            try:
                msg_time = datetime.fromisoformat(msg.get('sent_at', ''))
                if msg_time >= recent_date:
                    active_users.add(msg.get('sender', 'Unknown'))
            except Exception:
                continue

        return {
            'total_messages': total_messages,
            'total_users': len(unique_users),
            'active_users': len(active_users),
            'avg_messages_per_day': round(total_messages / days, 2)
        }

    def analyze_all_chats(self) -> Dict:
        """
        分析所有监控的群聊

        Returns:
            所有群聊的分析结果
        """
        try:
            # 获取所有群聊
            response = requests.get(f"{self.api_base_url}/api/chats")
            response.raise_for_status()
            chats = response.json()

            results = {}

            for chat in chats:
                if not chat.get('enabled', False):
                    continue

                chat_id = chat['id']
                chat_name = chat['chat_name']

                logger.info(f"分析群聊: {chat_name}")

                # 获取统计信息
                stats = self.get_chat_statistics(chat_id)
                user_stats = self.get_user_statistics(chat_id)

                results[chat_name] = {
                    'chat_stats': stats,
                    'user_stats': user_stats
                }

            return results

        except Exception as e:
            logger.error(f"分析失败: {e}")
            return {}


# 测试代码
if __name__ == "__main__":
    analyzer = ActivityAnalyzer()

    # 测试获取不活跃用户
    # inactive = analyzer.get_inactive_users(
    #     chat_id=1,
    #     inactive_days=7,
    #     min_messages_per_day=1
    # )
    # print(f"不活跃用户: {inactive}")

    # 测试获取用户统计
    # stats = analyzer.get_user_statistics(chat_id=1, days=30)
    # print(f"用户统计: {stats}")

    print("✅ 活跃度分析器已就绪")
