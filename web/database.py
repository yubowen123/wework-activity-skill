"""
数据库配置和连接
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "wework.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 数据库URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite需要
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI依赖注入：获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    上下文管理器：用于非FastAPI场景
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
