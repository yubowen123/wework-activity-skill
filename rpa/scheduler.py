"""
定时调度器模块
使用 APScheduler 定时执行消息采集和规则检查
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .message_collector import MessageCollector
from .rule_executor import RuleExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RPAScheduler:
    """RPA 定时调度器"""

    def __init__(self, api_base_url: str = "http://localhost:8000", debug: bool = False):
        """
        初始化调度器

        Args:
            api_base_url: 后端 API 地址
            debug: 是否开启调试模式
        """
        self.api_base_url = api_base_url
        self.debug = debug

        # 创建调度器
        self.scheduler = BackgroundScheduler(
            timezone='Asia/Shanghai',
            job_defaults={
                'coalesce': True,  # 合并错过的任务
                'max_instances': 1  # 同一任务最多1个实例运行
            }
        )

        # 创建子模块
        self.collector = MessageCollector(api_base_url, debug)
        self.executor = RuleExecutor(api_base_url, debug)

        logger.info("RPA 调度器已初始化")

    def collect_messages_job(self):
        """消息采集任务"""
        try:
            logger.info("=" * 50)
            logger.info("开始执行消息采集任务")
            logger.info(f"时间: {datetime.now()}")

            stats = self.collector.collect_all()

            logger.info("消息采集完成:")
            for chat_name, count in stats.items():
                logger.info(f"  {chat_name}: {count} 条消息")

            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"消息采集任务执行失败: {e}")

    def execute_rules_job(self, dry_run: bool = False):
        """规则执行任务"""
        try:
            logger.info("=" * 50)
            logger.info("开始执行规则检查任务")
            logger.info(f"时间: {datetime.now()}")
            logger.info(f"模式: {'模拟运行' if dry_run else '实际执行'}")

            results = self.executor.execute_all_rules(dry_run=dry_run)

            logger.info("规则执行完成:")
            for result in results:
                status = "✅" if result['success'] else "❌"
                logger.info(f"  {status} {result['rule_name']}: {result['message']}")

            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"规则执行任务失败: {e}")

    def add_message_collection_job(
        self,
        interval_minutes: int = None,
        cron_expression: str = None,
        job_id: str = "message_collection"
    ):
        """
        添加消息采集定时任务

        Args:
            interval_minutes: 间隔分钟数（与 cron_expression 二选一）
            cron_expression: Cron 表达式（与 interval_minutes 二选一）
            job_id: 任务ID
        """
        # 移除旧任务（如果存在）
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        if interval_minutes:
            # 使用间隔触发器
            trigger = IntervalTrigger(minutes=interval_minutes)
            logger.info(f"添加消息采集任务: 每 {interval_minutes} 分钟执行一次")

        elif cron_expression:
            # 使用 Cron 触发器
            trigger = CronTrigger.from_crontab(cron_expression, timezone='Asia/Shanghai')
            logger.info(f"添加消息采集任务: Cron={cron_expression}")

        else:
            # 默认：每小时执行一次
            trigger = IntervalTrigger(hours=1)
            logger.info("添加消息采集任务: 每小时执行一次")

        self.scheduler.add_job(
            self.collect_messages_job,
            trigger=trigger,
            id=job_id,
            name="消息采集任务",
            replace_existing=True
        )

    def add_rule_execution_job(
        self,
        check_time: str = "09:00",
        dry_run: bool = False,
        job_id: str = "rule_execution"
    ):
        """
        添加规则执行定时任务

        Args:
            check_time: 检查时间，格式 "HH:MM"
            dry_run: 是否为模拟运行
            job_id: 任务ID
        """
        # 移除旧任务（如果存在）
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        # 解析时间
        hour, minute = map(int, check_time.split(':'))

        # 使用 Cron 触发器：每天指定时间执行
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone='Asia/Shanghai'
        )

        logger.info(f"添加规则执行任务: 每天 {check_time} 执行（{'模拟' if dry_run else '实际'}）")

        self.scheduler.add_job(
            lambda: self.execute_rules_job(dry_run=dry_run),
            trigger=trigger,
            id=job_id,
            name="规则执行任务",
            replace_existing=True
        )

    def add_custom_job(self, func, trigger, job_id: str, name: str = None):
        """
        添加自定义任务

        Args:
            func: 要执行的函数
            trigger: 触发器（IntervalTrigger 或 CronTrigger）
            job_id: 任务ID
            name: 任务名称
        """
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=name or job_id,
            replace_existing=True
        )

        logger.info(f"添加自定义任务: {name or job_id}")

    def remove_job(self, job_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除任务: {job_id}")
        except Exception as e:
            logger.warning(f"移除任务失败: {e}")

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ RPA 调度器已启动")
            self.print_jobs()
        else:
            logger.warning("调度器已在运行")

    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("❌ RPA 调度器已停止")
        else:
            logger.warning("调度器未在运行")

    def print_jobs(self):
        """打印所有任务"""
        jobs = self.scheduler.get_jobs()

        if not jobs:
            logger.info("没有已安排的任务")
            return

        logger.info("已安排的任务:")
        for job in jobs:
            logger.info(f"  - {job.name} (ID: {job.id})")
            logger.info(f"    下次运行: {job.next_run_time}")

    def run_job_now(self, job_id: str):
        """立即运行指定任务"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.func()
                logger.info(f"已手动执行任务: {job_id}")
            else:
                logger.warning(f"任务不存在: {job_id}")
        except Exception as e:
            logger.error(f"执行任务失败: {e}")


# 默认配置示例
def create_default_scheduler(api_base_url: str = "http://localhost:8000", debug: bool = False) -> RPAScheduler:
    """
    创建带有默认任务的调度器

    Returns:
        配置好的调度器实例
    """
    scheduler = RPAScheduler(api_base_url, debug)

    # 添加消息采集任务：每2小时执行一次
    scheduler.add_message_collection_job(interval_minutes=120)

    # 添加规则执行任务：每天早上9点执行
    scheduler.add_rule_execution_job(check_time="09:00", dry_run=False)

    return scheduler


# 测试代码
if __name__ == "__main__":
    # 创建调度器
    scheduler = create_default_scheduler(debug=True)

    # 启动调度器
    scheduler.start()

    # 打印任务列表
    print("\n" + "=" * 50)
    scheduler.print_jobs()
    print("=" * 50)

    # 保持运行
    try:
        import time
        print("\n调度器运行中... (按 Ctrl+C 停止)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止调度器...")
        scheduler.stop()
        print("✅ 已停止")
