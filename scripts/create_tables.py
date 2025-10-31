"""
scripts/create_tables.py
---------------------------------
用于在 MySQL 中创建所有基础表（sources / companies / jobs）。
支持重新初始化数据库结构。
"""

from app.db import engine
from app.models import Base

if __name__ == "__main__":
    print("🚀 Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

