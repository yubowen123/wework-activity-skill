"""
RPA 配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# API 配置
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# 企业微信配置
WEWORK_APP_NAME = "企业微信"
WEWORK_BUNDLE_ID = "com.tencent.WeWorkMac"

# RPA 配置
RPA_DEBUG = os.getenv('RPA_DEBUG', 'false').lower() == 'true'
RPA_SCREENSHOT_DIR = BASE_DIR / "debug_screenshots"

# 调度器配置
SCHEDULER_TIMEZONE = 'Asia/Shanghai'

# 消息采集配置
MESSAGE_COLLECTION_INTERVAL_MINUTES = int(os.getenv('MESSAGE_COLLECTION_INTERVAL', '120'))  # 默认2小时

# 规则执行配置
RULE_EXECUTION_TIME = os.getenv('RULE_EXECUTION_TIME', '09:00')  # 默认每天9点
RULE_EXECUTION_DRY_RUN = os.getenv('RULE_EXECUTION_DRY_RUN', 'false').lower() == 'true'  # 默认实际执行

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 数据库配置（与后端保持一致）
DB_PATH = BASE_DIR / "data" / "wework.db"

# pyautogui 配置
PYAUTOGUI_PAUSE = 0.5  # 每次操作后暂停时间（秒）
PYAUTOGUI_FAILSAFE = True  # 鼠标移到角落停止

# OCR 配置（如果使用）
TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/local/bin/tesseract')
OCR_LANG = 'chi_sim+eng'  # 中文简体 + 英文

# 图像匹配置信度
IMAGE_MATCH_CONFIDENCE = 0.8

# 超时设置
AUTOMATION_TIMEOUT = 10  # 自动化操作超时（秒）
API_TIMEOUT = 30  # API 请求超时（秒）

# 消息采集设置
MAX_MESSAGES_PER_CHAT = 1000  # 每个群聊最多采集的消息数
MESSAGE_SCROLL_COUNT = 5  # 每次滚动次数


def get_config():
    """获取配置字典"""
    return {
        'api_base_url': API_BASE_URL,
        'debug': RPA_DEBUG,
        'message_collection_interval': MESSAGE_COLLECTION_INTERVAL_MINUTES,
        'rule_execution_time': RULE_EXECUTION_TIME,
        'rule_execution_dry_run': RULE_EXECUTION_DRY_RUN,
    }


def print_config():
    """打印当前配置"""
    config = get_config()
    print("=" * 50)
    print("RPA 配置:")
    print("=" * 50)
    for key, value in config.items():
        print(f"  {key}: {value}")
    print("=" * 50)


if __name__ == "__main__":
    print_config()
