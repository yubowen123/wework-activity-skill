"""
RPA 控制 API
提供 Web 界面控制 RPA 的接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局 RPA 调度器实例（由 gui_app_simple.py 注入）
_rpa_scheduler = None


def set_rpa_scheduler(scheduler):
    """设置 RPA 调度器实例"""
    global _rpa_scheduler
    _rpa_scheduler = scheduler


class RPAStatusResponse(BaseModel):
    """RPA 状态响应"""
    running: bool
    message: str
    jobs: List[Dict]


class RPATestResponse(BaseModel):
    """RPA 测试响应"""
    success: bool
    message: str
    details: Optional[Dict] = None


class ManualExecuteRequest(BaseModel):
    """手动执行请求"""
    dry_run: bool = True
    rule_id: Optional[int] = None


@router.get("/status", response_model=RPAStatusResponse)
def get_rpa_status():
    """获取 RPA 运行状态"""
    if _rpa_scheduler is None:
        return RPAStatusResponse(
            running=False,
            message="RPA 调度器未启动",
            jobs=[]
        )

    try:
        jobs = _rpa_scheduler.scheduler.get_jobs()
        job_list = []

        for job in jobs:
            job_list.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })

        return RPAStatusResponse(
            running=_rpa_scheduler.scheduler.running,
            message="RPA 调度器运行中",
            jobs=job_list
        )
    except Exception as e:
        logger.error(f"获取 RPA 状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-wework", response_model=RPATestResponse)
def test_wework_connection():
    """测试企业微信连接"""
    try:
        from rpa.wework_automation import WeWorkAutomation

        automation = WeWorkAutomation(debug=True)

        # 检查企业微信是否运行
        is_running = automation.is_running()

        if is_running:
            # 尝试激活窗口
            activated = automation.activate_app()

            # 截图测试
            screenshot_path = automation.take_screenshot("web_test")

            return RPATestResponse(
                success=True,
                message="企业微信连接正常",
                details={
                    "running": True,
                    "activated": activated,
                    "screenshot": screenshot_path
                }
            )
        else:
            return RPATestResponse(
                success=False,
                message="企业微信未运行，请先启动企业微信客户端",
                details={"running": False}
            )

    except Exception as e:
        logger.error(f"测试企业微信连接失败: {e}")
        return RPATestResponse(
            success=False,
            message=f"测试失败: {str(e)}",
            details={"error": str(e)}
        )


@router.post("/test-chat")
def test_open_chat(chat_name: str):
    """测试打开指定群聊"""
    try:
        from rpa.wework_automation import WeWorkAutomation

        automation = WeWorkAutomation(debug=True)

        if not automation.is_running():
            raise HTTPException(status_code=400, detail="企业微信未运行")

        # 尝试打开群聊
        success = automation.search_chat(chat_name)

        if success:
            # 截图
            screenshot_path = automation.take_screenshot(f"chat_{chat_name}")

            return RPATestResponse(
                success=True,
                message=f"成功打开群聊: {chat_name}",
                details={
                    "chat_name": chat_name,
                    "screenshot": screenshot_path
                }
            )
        else:
            return RPATestResponse(
                success=False,
                message=f"打开群聊失败: {chat_name}",
                details={"chat_name": chat_name}
            )

    except Exception as e:
        logger.error(f"测试打开群聊失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-now")
def collect_messages_now(chat_name: Optional[str] = None):
    """立即采集消息"""
    try:
        from rpa.message_collector import MessageCollector

        collector = MessageCollector(debug=True)

        if chat_name:
            # 采集指定群聊
            messages = collector.collect_messages_from_chat(chat_name)
            return {
                "success": True,
                "message": f"采集完成: {chat_name}",
                "count": len(messages)
            }
        else:
            # 采集所有群聊
            stats = collector.collect_all()
            return {
                "success": True,
                "message": "采集完成",
                "stats": stats
            }

    except Exception as e:
        logger.error(f"采集消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-rules", response_model=Dict)
def execute_rules_now(request: ManualExecuteRequest):
    """立即执行规则"""
    try:
        from rpa.rule_executor import RuleExecutor

        executor = RuleExecutor(debug=True)

        if request.rule_id:
            # 执行指定规则
            result = executor.execute_rule_by_id(request.rule_id, dry_run=request.dry_run)
            return {
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "results": [result]
            }
        else:
            # 执行所有规则
            results = executor.execute_all_rules(dry_run=request.dry_run)
            return {
                "success": True,
                "message": f"执行了 {len(results)} 条规则",
                "results": results
            }

    except Exception as e:
        logger.error(f"执行规则失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart")
def restart_rpa_scheduler():
    """重启 RPA 调度器"""
    if _rpa_scheduler is None:
        raise HTTPException(status_code=400, detail="RPA 调度器未初始化")

    try:
        # 停止调度器
        _rpa_scheduler.stop()

        import time
        time.sleep(1)

        # 重新启动
        _rpa_scheduler.start()

        return {
            "success": True,
            "message": "RPA 调度器已重启"
        }
    except Exception as e:
        logger.error(f"重启 RPA 调度器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
def get_rpa_logs(limit: int = 50):
    """获取 RPA 日志（暂未实现完整日志系统）"""
    return {
        "success": True,
        "message": "日志功能开发中",
        "logs": []
    }
