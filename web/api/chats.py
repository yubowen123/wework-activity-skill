"""
群聊管理API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import MonitoredChat, Rule, Whitelist
from ..schemas import ChatCreate, ChatUpdate, ChatResponse, MessageResponse

router = APIRouter()


@router.get("/", response_model=List[ChatResponse])
def get_chats(
    enabled_only: bool = False,
    db: Session = Depends(get_db)
):
    """获取所有监控的群聊"""
    query = db.query(MonitoredChat)

    if enabled_only:
        query = query.filter(MonitoredChat.enabled == True)

    chats = query.all()

    # 添加统计信息
    result = []
    for chat in chats:
        chat_dict = {
            "id": chat.id,
            "chat_name": chat.chat_name,
            "chat_id": chat.chat_id,
            "enabled": chat.enabled,
            "auto_remove": chat.auto_remove,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at,
            "rules_count": len(chat.rules),
            "whitelist_count": len(chat.whitelist),
            "active_rules": len([r for r in chat.rules if r.enabled])
        }
        result.append(ChatResponse(**chat_dict))

    return result


@router.post("/", response_model=ChatResponse)
def create_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db)
):
    """添加监控群聊"""
    # 检查是否已存在
    existing = db.query(MonitoredChat).filter(
        MonitoredChat.chat_name == chat.chat_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="群聊已存在")

    # 创建
    db_chat = MonitoredChat(
        chat_name=chat.chat_name,
        chat_id=chat.chat_id,
        enabled=chat.enabled,
        auto_remove=chat.auto_remove
    )

    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    return ChatResponse(
        id=db_chat.id,
        chat_name=db_chat.chat_name,
        chat_id=db_chat.chat_id,
        enabled=db_chat.enabled,
        auto_remove=db_chat.auto_remove,
        created_at=db_chat.created_at,
        updated_at=db_chat.updated_at,
        rules_count=0,
        whitelist_count=0,
        active_rules=0
    )


@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: int,
    db: Session = Depends(get_db)
):
    """获取单个群聊详情"""
    chat = db.query(MonitoredChat).filter(MonitoredChat.id == chat_id).first()

    if not chat:
        raise HTTPException(status_code=404, detail="群聊不存在")

    return ChatResponse(
        id=chat.id,
        chat_name=chat.chat_name,
        chat_id=chat.chat_id,
        enabled=chat.enabled,
        auto_remove=chat.auto_remove,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        rules_count=len(chat.rules),
        whitelist_count=len(chat.whitelist),
        active_rules=len([r for r in chat.rules if r.enabled])
    )


@router.put("/{chat_id}", response_model=ChatResponse)
def update_chat(
    chat_id: int,
    chat: ChatUpdate,
    db: Session = Depends(get_db)
):
    """更新群聊配置"""
    db_chat = db.query(MonitoredChat).filter(MonitoredChat.id == chat_id).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="群聊不存在")

    # 更新字段
    update_data = chat.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_chat, key, value)

    db_chat.updated_at = datetime.now()

    db.commit()
    db.refresh(db_chat)

    return ChatResponse(
        id=db_chat.id,
        chat_name=db_chat.chat_name,
        chat_id=db_chat.chat_id,
        enabled=db_chat.enabled,
        auto_remove=db_chat.auto_remove,
        created_at=db_chat.created_at,
        updated_at=db_chat.updated_at,
        rules_count=len(db_chat.rules),
        whitelist_count=len(db_chat.whitelist),
        active_rules=len([r for r in db_chat.rules if r.enabled])
    )


@router.delete("/{chat_id}", response_model=MessageResponse)
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db)
):
    """删除监控群聊"""
    db_chat = db.query(MonitoredChat).filter(MonitoredChat.id == chat_id).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="群聊不存在")

    db.delete(db_chat)
    db.commit()

    return MessageResponse(message="删除成功")


@router.post("/{chat_id}/toggle")
def toggle_chat(
    chat_id: int,
    db: Session = Depends(get_db)
):
    """启用/禁用群聊监控"""
    db_chat = db.query(MonitoredChat).filter(MonitoredChat.id == chat_id).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="群聊不存在")

    db_chat.enabled = not db_chat.enabled
    db_chat.updated_at = datetime.now()

    db.commit()

    return {
        "chat_id": chat_id,
        "enabled": db_chat.enabled,
        "message": f"已{'启用' if db_chat.enabled else '禁用'}群聊监控"
    }
