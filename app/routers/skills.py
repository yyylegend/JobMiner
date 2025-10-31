# app/routers/skills.py
from fastapi import APIRouter, Query
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Job
from collections import Counter
import re

router = APIRouter(prefix="/api/skills", tags=["Skills"])

@router.get("/top")
async def get_top_skills(limit: int = Query(10, ge=1, le=50)):
    """
    统计职位描述中出现次数最多的技能关键词。
    limit 参数控制返回前多少个技能（默认10）。
    """

    db = SessionLocal()

    try:
        # 1️⃣ 从数据库读取所有职位描述
        results = db.execute(select(Job.description)).scalars().all()

        # 2️⃣ 定义我们要匹配的技能关键词（可自行扩展）
        skills_list = [
            "Python", "SQL", "Spark", "Kafka", "Hadoop", "Flink", "Pandas", "Numpy",
            "TensorFlow", "PyTorch", "Docker", "Kubernetes", "AWS", "Azure", "Linux"
        ]

        # 3️⃣ 统计出现次数
        counter = Counter()
        for desc in results:
            if not desc:
                continue
            for skill in skills_list:
                # 使用正则匹配（忽略大小写）
                if re.search(rf"\b{skill}\b", desc, flags=re.IGNORECASE):
                    counter[skill] += 1

        # 4️⃣ 构造返回结果
        top_skills = [
            {"skill": skill, "count": count}
            for skill, count in counter.most_common(limit)
        ]

        return {"top_skills": top_skills}

    finally:
        db.close()