# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 创建 ORM 基类
Base = declarative_base()

# 如果使用 SQLite 要额外参数，否则 MySQL 可以为空
connect_args = {}
if settings.DB_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# 创建数据库引擎
engine = create_engine(
    settings.DB_URL,
    pool_pre_ping=True,
    connect_args=connect_args
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
