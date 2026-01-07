"""
白名单管理API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Whitelist, MonitoredChat
from ..schemas import WhitelistCreate, WhitelistResponse, WhitelistBatchCreate, MessageResponse

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=List[WhitelistResponse])
def get_chat_whitelist(
    chat_id: int,
    db: Session = Depends(get_db)
):
    """获取群聊白名单"""
    whitelist = db.query(Whitelist).filter(Whitelist.chat_id == chat_id).all()
    return whitelist


@router.post("/", response_model=WhitelistResponse)
def add_to_whitelist(
    item: WhitelistCreate,
    db: Session = Depends(get_db)
):
    """添加到白名单"""
    # 检查群聊是否存在
    chat = db.query(MonitoredChat).filter(MonitoredChat.id == item.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="群聊不存在")

    # 检查是否已存在
    existing = db.query(Whitelist).filter(
        Whitelist.chat_id == item.chat_id,
        Whitelist.user_name == item.user_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="用户已在白名单中")

    # 创建
    db_item = Whitelist(
        chat_id=item.chat_id,
        user_name=item.user_name,
        user_id=item.user_id,
        reason=item.reason,
        added_by=item.added_by
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


@router.delete("/{whitelist_id}", response_model=MessageResponse)
def remove_from_whitelist(
    whitelist_id: int,
    db: Session = Depends(get_db)
):
    """从白名单移除"""
    db_item = db.query(Whitelist).filter(Whitelist.id == whitelist_id).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="白名单记录不存在")

    db.delete(db_item)
    db.commit()

    return MessageResponse(message="删除成功")


@router.post("/batch")
def batch_add_to_whitelist(
    data: WhitelistBatchCreate,
    db: Session = Depends(get_db)
):
    """批量添加到白名单"""
    # 检查群聊是否存在
    chat = db.query(MonitoredChat).filter(MonitoredChat.id == data.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="群聊不存在")

    added = []
    skipped = []

    for user_name in data.user_names:
        # 检查是否已存在
        existing = db.query(Whitelist).filter(
            Whitelist.chat_id == data.chat_id,
            Whitelist.user_name == user_name
        ).first()

        if existing:
            skipped.append(user_name)
            continue

        # 创建
        db_item = Whitelist(
            chat_id=data.chat_id,
            user_name=user_name,
            reason=data.reason,
            added_by=data.added_by
        )

        db.add(db_item)
        added.append(user_name)

    db.commit()

    return {
        "added": len(added),
        "skipped": len(skipped),
        "added_users": added,
        "skipped_users": skipped,
        "message": f"成功添加 {len(added)} 人，跳过 {len(skipped)} 人"
    }
