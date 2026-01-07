#!/usr/bin/env python3
"""
RPA 主程序 - 企业微信活跃度管理自动化
"""

import sys
import time
import argparse
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rpa.config import get_config, print_config
from rpa.scheduler import RPAScheduler, create_default_scheduler
from rpa.message_collector import MessageCollector
from rpa.rule_executor import RuleExecutor
from rpa.wework_automation import WeWorkAutomation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def start_scheduler(args):
    """启动调度器模式"""
    config = get_config()

    logger.info("=" * 50)
    logger.info("启动 RPA 调度器")
    logger.info("=" * 50)

    # 创建调度器
    scheduler = create_default_scheduler(
        api_base_url=config['api_base_url'],
        debug=args.debug or config['debug']
    )

    # 启动调度器
    scheduler.start()

    # 保持运行
    try:
        logger.info("\n✅ 调度器运行中... (按 Ctrl+C 停止)\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n正在停止调度器...")
        scheduler.stop()
        logger.info("✅ 调度器已停止")


def collect_messages(args):
    """手动采集消息"""
    config = get_config()

    logger.info("=" * 50)
    logger.info("手动采集消息")
    logger.info("=" * 50)

    collector = MessageCollector(
        api_base_url=config['api_base_url'],
        debug=args.debug or config['debug']
    )

    if args.chat:
        # 采集指定群聊
        logger.info(f"采集群聊: {args.chat}")
        messages = collector.collect_messages_from_chat(args.chat)
        logger.info(f"采集到 {len(messages)} 条消息")
    else:
        # 采集所有群聊
        stats = collector.collect_all()
        logger.info("采集结果:")
        for chat_name, count in stats.items():
            logger.info(f"  {chat_name}: {count} 条消息")


def execute_rules(args):
    """手动执行规则"""
    config = get_config()

    logger.info("=" * 50)
    logger.info("手动执行规则")
    logger.info(f"模式: {'模拟运行' if args.dry_run else '实际执行'}")
    logger.info("=" * 50)

    executor = RuleExecutor(
        api_base_url=config['api_base_url'],
        debug=args.debug or config['debug']
    )

    if args.rule_id:
        # 执行指定规则
        result = executor.execute_rule_by_id(args.rule_id, dry_run=args.dry_run)
        status = "✅" if result['success'] else "❌"
        logger.info(f"{status} 规则执行结果: {result['message']}")
        if result.get('affected_users'):
            logger.info(f"受影响用户: {', '.join(result['affected_users'])}")
    else:
        # 执行所有规则
        results = executor.execute_all_rules(dry_run=args.dry_run)
        logger.info(f"执行了 {len(results)} 条规则:")
        for result in results:
            status = "✅" if result['success'] else "❌"
            logger.info(f"  {status} {result.get('rule_name', 'Unknown')}: {result['message']}")


def test_automation(args):
    """测试企业微信自动化"""
    logger.info("=" * 50)
    logger.info("测试企业微信自动化")
    logger.info("=" * 50)

    automation = WeWorkAutomation(debug=True)

    # 测试启动
    if automation.is_running():
        logger.info("✅ 企业微信正在运行")
    else:
        logger.info("企业微信未运行，尝试启动...")
        if automation.launch_app():
            logger.info("✅ 企业微信已启动")
        else:
            logger.error("❌ 启动失败")
            return

    # 测试搜索群聊
    if args.chat:
        logger.info(f"尝试打开群聊: {args.chat}")
        if automation.search_chat(args.chat):
            logger.info("✅ 群聊已打开")
        else:
            logger.error("❌ 打开群聊失败")

    # 测试截图
    screenshot_path = automation.take_screenshot("test")
    if screenshot_path:
        logger.info(f"✅ 截图已保存: {screenshot_path}")


def import_messages(args):
    """从文本文件导入消息"""
    config = get_config()

    logger.info("=" * 50)
    logger.info("从文件导入消息")
    logger.info("=" * 50)

    if not args.file:
        logger.error("请指定文件路径: --file <path>")
        return

    if not args.chat:
        logger.error("请指定群聊名称: --chat <name>")
        return

    collector = MessageCollector(
        api_base_url=config['api_base_url'],
        debug=args.debug or config['debug']
    )

    count = collector.import_from_text_file(args.chat, args.file)
    logger.info(f"✅ 成功导入 {count} 条消息")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='企业微信活跃度管理 RPA 自动化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动调度器（定时执行）
  python -m rpa.main scheduler

  # 手动采集所有群聊消息
  python -m rpa.main collect

  # 手动采集指定群聊
  python -m rpa.main collect --chat "技术交流群"

  # 模拟执行所有规则（不实际踢人）
  python -m rpa.main execute --dry-run

  # 实际执行所有规则
  python -m rpa.main execute

  # 执行指定规则
  python -m rpa.main execute --rule-id 1

  # 测试企业微信自动化
  python -m rpa.main test --chat "测试群"

  # 从文件导入消息
  python -m rpa.main import --chat "技术交流群" --file messages.txt

  # 显示配置
  python -m rpa.main config
        """
    )

    parser.add_argument('--debug', action='store_true', help='开启调试模式')

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # scheduler 命令
    parser_scheduler = subparsers.add_parser('scheduler', help='启动调度器（定时执行）')

    # collect 命令
    parser_collect = subparsers.add_parser('collect', help='采集消息')
    parser_collect.add_argument('--chat', help='指定群聊名称')

    # execute 命令
    parser_execute = subparsers.add_parser('execute', help='执行规则')
    parser_execute.add_argument('--rule-id', type=int, help='指定规则ID')
    parser_execute.add_argument('--dry-run', action='store_true', help='模拟运行（不实际踢人）')

    # test 命令
    parser_test = subparsers.add_parser('test', help='测试企业微信自动化')
    parser_test.add_argument('--chat', help='测试打开的群聊名称')

    # import 命令
    parser_import = subparsers.add_parser('import', help='从文件导入消息')
    parser_import.add_argument('--chat', required=True, help='群聊名称')
    parser_import.add_argument('--file', required=True, help='文本文件路径')

    # config 命令
    parser_config = subparsers.add_parser('config', help='显示配置')

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 执行命令
    if args.command == 'scheduler':
        start_scheduler(args)
    elif args.command == 'collect':
        collect_messages(args)
    elif args.command == 'execute':
        execute_rules(args)
    elif args.command == 'test':
        test_automation(args)
    elif args.command == 'import':
        import_messages(args)
    elif args.command == 'config':
        print_config()


if __name__ == "__main__":
    main()
