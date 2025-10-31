# app/routers/stats.py
from fastapi import APIRouter
from sqlalchemy import func, select
from app.db import SessionLocal
from app.models import Job

router = APIRouter(prefix="/api/stats", tags=["Statistics"])

@router.get("/salary")
async def salary_stats():
    """
    统计每个城市的平均最低薪资、平均最高薪资和中位薪资。
    """
    db = SessionLocal()
    try:
        # 聚合查询：分组统计每个城市的平均值
        stmt = (
            select(
                Job.location_city.label("city"),
                func.avg(Job.salary_min).label("avg_min"),
                func.avg(Job.salary_max).label("avg_max"),
                func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_mid"),
            )
            .where(Job.salary_min.isnot(None), Job.salary_max.isnot(None))
            .group_by(Job.location_city)
        )

        results = db.execute(stmt).all()

        # 构造成字典格式输出
        data = {
            row.city: {
                "avg_min": float(row.avg_min),
                "avg_max": float(row.avg_max),
                "avg_mid": float(row.avg_mid),
            }
            for row in results
            if row.city is not None
        }

        return data
    finally:
        db.close()
