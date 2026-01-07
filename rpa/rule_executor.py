"""
规则执行器模块
根据配置的规则检查并执行相应操作（如踢出不活跃用户）
"""

import requests
import logging
from datetime import datetime
from typing import List, Dict
from .activity_analyzer import ActivityAnalyzer
from .wework_automation import WeWorkAutomation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleExecutor:
    """规则执行器"""

    def __init__(self, api_base_url: str = "http://localhost:8000", debug: bool = False):
        """
        初始化规则执行器

        Args:
            api_base_url: 后端 API 地址
            debug: 是否开启调试模式
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.analyzer = ActivityAnalyzer(api_base_url)
        self.automation = WeWorkAutomation(debug=debug)

    def get_active_rules(self) -> List[Dict]:
        """
        获取所有启用的规则

        Returns:
            规则列表
        """
        try:
            response = requests.get(f"{self.api_base_url}/api/rules")
            response.raise_for_status()
            rules = response.json()

            # 过滤启用的规则
            active_rules = [rule for rule in rules if rule.get('enabled', False)]

            logger.info(f"获取到 {len(active_rules)} 条启用的规则")
            return active_rules

        except Exception as e:
            logger.error(f"获取规则失败: {e}")
            return []

    def get_whitelist(self, chat_id: int) -> List[str]:
        """
        获取指定群聊的白名单用户

        Args:
            chat_id: 群聊ID

        Returns:
            白名单用户名列表
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/api/whitelist",
                params={"chat_id": chat_id}
            )
            response.raise_for_status()
            whitelist = response.json()

            user_names = [item['user_name'] for item in whitelist]

            logger.info(f"群聊 {chat_id} 的白名单有 {len(user_names)} 个用户")
            return user_names

        except Exception as e:
            logger.error(f"获取白名单失败: {e}")
            return []

    def execute_rule(self, rule: Dict, dry_run: bool = False) -> Dict:
        """
        执行单个规则

        Args:
            rule: 规则字典
            dry_run: 是否为模拟运行（不实际踢人）

        Returns:
            执行结果
        """
        rule_id = rule['id']
        rule_name = rule['rule_name']
        chat_id = rule['chat_id']
        inactive_days = rule['inactive_days']
        min_messages = rule['min_messages_per_day']
        auto_execute = rule.get('auto_execute', False)

        logger.info(f"执行规则: {rule_name} (ID: {rule_id})")

        result = {
            'rule_id': rule_id,
            'rule_name': rule_name,
            'chat_id': chat_id,
            'executed_at': datetime.now().isoformat(),
            'affected_users': [],
            'success': False,
            'message': ''
        }

        try:
            # 获取不活跃用户
            inactive_users = self.analyzer.get_inactive_users(
                chat_id=chat_id,
                inactive_days=inactive_days,
                min_messages_per_day=min_messages
            )

            if not inactive_users:
                result['message'] = '没有不活跃用户'
                result['success'] = True
                logger.info(f"规则 {rule_name}: 没有不活跃用户")
                return result

            # 获取白名单
            whitelist = self.get_whitelist(chat_id)

            # 过滤白名单用户
            users_to_remove = [
                user for user in inactive_users
                if user['user_name'] not in whitelist
            ]

            if not users_to_remove:
                result['message'] = '所有不活跃用户都在白名单中'
                result['success'] = True
                logger.info(f"规则 {rule_name}: 所有不活跃用户都在白名单中")
                return result

            result['affected_users'] = [user['user_name'] for user in users_to_remove]

            # 如果是模拟运行或规则未设置自动执行
            if dry_run or not auto_execute:
                result['message'] = f'模拟运行：找到 {len(users_to_remove)} 个需要移除的用户'
                result['success'] = True
                logger.info(f"规则 {rule_name}: {result['message']}")
                logger.info(f"待移除用户: {result['affected_users']}")
                return result

            # 实际执行移除操作
            success_count = 0
            failed_users = []

            # 获取群聊信息
            chat_response = requests.get(f"{self.api_base_url}/api/chats/{chat_id}")
            chat_response.raise_for_status()
            chat = chat_response.json()
            chat_name = chat['chat_name']

            # 确保企业微信正在运行
            if not self.automation.is_running():
                if not self.automation.launch_app():
                    result['message'] = '无法启动企业微信'
                    logger.error(result['message'])
                    return result

            # 打开群聊
            if not self.automation.search_chat(chat_name):
                result['message'] = f'无法打开群聊: {chat_name}'
                logger.error(result['message'])
                return result

            # 逐个移除用户
            for user in users_to_remove:
                user_name = user['user_name']
                logger.info(f"尝试移除用户: {user_name}")

                # 调用自动化模块移除用户
                if self.automation.remove_member(user_name):
                    success_count += 1
                    logger.info(f"✅ 成功移除用户: {user_name}")
                else:
                    failed_users.append(user_name)
                    logger.warning(f"❌ 移除用户失败: {user_name}")

            # 更新结果
            result['success'] = success_count > 0
            result['message'] = f'成功移除 {success_count}/{len(users_to_remove)} 个用户'

            if failed_users:
                result['message'] += f'，失败: {", ".join(failed_users)}'

            logger.info(f"规则 {rule_name} 执行完成: {result['message']}")

        except Exception as e:
            result['message'] = f'执行失败: {str(e)}'
            logger.error(f"规则 {rule_name} 执行出错: {e}")

        return result

    def save_execution_result(self, result: Dict):
        """
        保存规则执行结果到数据库

        Args:
            result: 执行结果字典
        """
        try:
            data = {
                "rule_id": result['rule_id'],
                "executed_at": result['executed_at'],
                "affected_users": ','.join(result['affected_users']),
                "success": result['success'],
                "message": result['message']
            }

            response = requests.post(
                f"{self.api_base_url}/api/executions",
                json=data
            )

            if response.status_code == 201:
                logger.info("执行结果已保存")
            else:
                logger.warning(f"保存执行结果失败: {response.text}")

        except Exception as e:
            logger.error(f"保存执行结果失败: {e}")

    def execute_all_rules(self, dry_run: bool = False) -> List[Dict]:
        """
        执行所有启用的规则

        Args:
            dry_run: 是否为模拟运行

        Returns:
            所有规则的执行结果列表
        """
        rules = self.get_active_rules()

        if not rules:
            logger.info("没有需要执行的规则")
            return []

        results = []

        for rule in rules:
            # 执行规则
            result = self.execute_rule(rule, dry_run=dry_run)
            results.append(result)

            # 保存执行结果（即使是模拟运行也保存）
            self.save_execution_result(result)

        logger.info(f"所有规则执行完成，共 {len(results)} 条")
        return results

    def execute_rule_by_id(self, rule_id: int, dry_run: bool = False) -> Dict:
        """
        执行指定ID的规则

        Args:
            rule_id: 规则ID
            dry_run: 是否为模拟运行

        Returns:
            执行结果
        """
        try:
            response = requests.get(f"{self.api_base_url}/api/rules/{rule_id}")
            response.raise_for_status()
            rule = response.json()

            result = self.execute_rule(rule, dry_run=dry_run)
            self.save_execution_result(result)

            return result

        except Exception as e:
            logger.error(f"执行规则 {rule_id} 失败: {e}")
            return {
                'rule_id': rule_id,
                'success': False,
                'message': f'执行失败: {str(e)}'
            }


# 测试代码
if __name__ == "__main__":
    executor = RuleExecutor(debug=True)

    # 测试执行所有规则（模拟运行）
    results = executor.execute_all_rules(dry_run=True)

    print("\n执行结果:")
    for result in results:
        print(f"  规则: {result['rule_name']}")
        print(f"  状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
        print(f"  消息: {result['message']}")
        print(f"  受影响用户: {result['affected_users']}")
        print()
