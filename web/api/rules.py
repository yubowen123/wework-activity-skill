"""
规则管理API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Rule, MonitoredChat
from ..schemas import RuleCreate, RuleUpdate, RuleResponse, MessageResponse

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=List[RuleResponse])
def get_chat_rules(
    chat_id: int,
    db: Session = Depends(get_db)
):
    """获取群聊的所有规则"""
    rules = db.query(Rule).filter(
        Rule.chat_id == chat_id
    ).order_by(Rule.priority.desc()).all()

    return rules


@router.post("/", response_model=RuleResponse)
def create_rule(
    rule: RuleCreate,
    db: Session = Depends(get_db)
):
    """创建规则"""
    # 检查群聊是否存在
    chat = db.query(MonitoredChat).filter(MonitoredChat.id == rule.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="群聊不存在")

    # 创建规则
    db_rule = Rule(
        chat_id=rule.chat_id,
        rule_name=rule.rule_name,
        rule_type=rule.rule_type,
        rule_config=rule.rule_config,
        priority=rule.priority,
        enabled=rule.enabled
    )

    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """获取规则详情"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: int,
    rule: RuleUpdate,
    db: Session = Depends(get_db)
):
    """更新规则"""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()

    if not db_rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    update_data = rule.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)

    db.commit()
    db.refresh(db_rule)

    return db_rule


@router.delete("/{rule_id}", response_model=MessageResponse)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """删除规则"""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()

    if not db_rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    db.delete(db_rule)
    db.commit()

    return MessageResponse(message="删除成功")


@router.post("/{rule_id}/toggle")
def toggle_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """启用/禁用规则"""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()

    if not db_rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    db_rule.enabled = not db_rule.enabled
    db.commit()

    return {
        "rule_id": rule_id,
        "enabled": db_rule.enabled,
        "message": f"已{'启用' if db_rule.enabled else '禁用'}规则"
    }


@router.get("/templates/list")
def get_rule_templates():
    """获取规则模板"""
    return [
        {
            "name": "连续N天不活跃",
            "type": "inactive_consecutive_days",
            "description": "连续N天没有发送消息的用户",
            "config_schema": {
                "days": {
                    "type": "number",
                    "label": "天数",
                    "default": 7,
                    "min": 1,
                    "max": 90
                }
            }
        },
        {
            "name": "月度最少消息数",
            "type": "monthly_min_messages",
            "description": "当月消息数少于指定数量",
            "config_schema": {
                "min_messages": {
                    "type": "number",
                    "label": "最少消息数",
                    "default": 10,
                    "min": 1
                }
            }
        },
        {
            "name": "月度最少活跃天数",
            "type": "monthly_min_active_days",
            "description": "当月活跃天数少于指定天数",
            "config_schema": {
                "min_active_days": {
                    "type": "number",
                    "label": "最少活跃天数",
                    "default": 5,
                    "min": 1,
                    "max": 31
                }
            }
        },
        {
            "name": "周度最少消息数",
            "type": "weekly_min_messages",
            "description": "本周消息数少于指定数量",
            "config_schema": {
                "min_messages": {
                    "type": "number",
                    "label": "最少消息数",
                    "default": 3,
                    "min": 1
                }
            }
        },
        {
            "name": "长期潜水",
            "type": "long_term_inactive",
            "description": "超过N天总消息数少于M条",
            "config_schema": {
                "days": {
                    "type": "number",
                    "label": "天数",
                    "default": 30,
                    "min": 1
                },
                "max_messages": {
                    "type": "number",
                    "label": "最大消息数",
                    "default": 5,
                    "min": 0
                }
            }
        }
    ]
