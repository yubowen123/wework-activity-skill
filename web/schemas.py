"""
Pydantic Schemas - API请求/响应数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ==================== 群聊相关 ====================

class ChatBase(BaseModel):
    chat_name: str
    chat_id: Optional[str] = None
    enabled: bool = True
    auto_remove: bool = False


class ChatCreate(ChatBase):
    pass


class ChatUpdate(BaseModel):
    chat_name: Optional[str] = None
    chat_id: Optional[str] = None
    enabled: Optional[bool] = None
    auto_remove: Optional[bool] = None


class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime
    rules_count: Optional[int] = 0
    whitelist_count: Optional[int] = 0
    active_rules: Optional[int] = 0

    class Config:
        from_attributes = True


# ==================== 规则相关 ====================

class RuleBase(BaseModel):
    chat_id: int
    rule_name: str
    rule_type: str
    rule_config: Dict[str, Any]
    priority: int = 0
    enabled: bool = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    rule_type: Optional[str] = None
    rule_config: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None


class RuleResponse(RuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 白名单相关 ====================

class WhitelistBase(BaseModel):
    chat_id: int
    user_name: str
    user_id: Optional[str] = None
    reason: Optional[str] = None
    added_by: Optional[str] = None


class WhitelistCreate(WhitelistBase):
    pass


class WhitelistResponse(WhitelistBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WhitelistBatchCreate(BaseModel):
    chat_id: int
    user_names: List[str]
    reason: Optional[str] = None
    added_by: Optional[str] = None


# ==================== 通用响应 ====================

class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
