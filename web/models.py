"""
数据库模型定义
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class MonitoredChat(Base):
    """监控群聊"""
    __tablename__ = 'monitored_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_name = Column(String(100), unique=True, nullable=False)
    chat_id = Column(String(100))
    enabled = Column(Boolean, default=True)
    auto_remove = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    rules = relationship("Rule", back_populates="chat", cascade="all, delete-orphan")
    whitelist = relationship("Whitelist", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chat")


class Rule(Base):
    """规则配置"""
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('monitored_chats.id'), nullable=False)
    rule_name = Column(String(100), nullable=False)
    rule_type = Column(String(50), nullable=False)
    rule_config = Column(JSON, nullable=False)
    priority = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    chat = relationship("MonitoredChat", back_populates="rules")


class Whitelist(Base):
    """白名单"""
    __tablename__ = 'whitelist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('monitored_chats.id'), nullable=False)
    user_name = Column(String(100), nullable=False)
    user_id = Column(String(100))
    reason = Column(String(200))
    added_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    chat = relationship("MonitoredChat", back_populates="whitelist")


class Message(Base):
    """消息记录"""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('monitored_chats.id'), nullable=False)
    chat_name = Column(String(100), nullable=False)
    user_name = Column(String(100), nullable=False)
    user_id = Column(String(100))
    message_type = Column(String(20))
    content = Column(Text)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    chat = relationship("MonitoredChat", back_populates="messages")


class RuleExecution(Base):
    """规则执行记录"""
    __tablename__ = 'rule_executions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('monitored_chats.id'), nullable=False)
    rule_id = Column(Integer, ForeignKey('rules.id'), nullable=False)
    violation_users = Column(JSON)
    removed_users = Column(JSON)
    execution_status = Column(String(20))
    execution_mode = Column(String(20))
    executed_at = Column(DateTime, default=datetime.now)
