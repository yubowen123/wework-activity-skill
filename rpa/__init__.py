"""
企业微信 RPA 自动化模块
"""

from .wework_automation import WeWorkAutomation
from .message_collector import MessageCollector
from .activity_analyzer import ActivityAnalyzer
from .rule_executor import RuleExecutor
from .scheduler import RPAScheduler

__all__ = [
    'WeWorkAutomation',
    'MessageCollector',
    'ActivityAnalyzer',
    'RuleExecutor',
    'RPAScheduler'
]
