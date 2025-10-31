from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.db import SessionLocal
from app.models import Job, Company

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# 获取数据库 Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/salary/average")
def average_salary(db: Session = Depends(get_db)):
    """计算各城市平均薪资（过滤异常值）"""
    # 过滤薪资异常（> 100000）和缺失
    stmt = (
        select(
            Job.location_city,
            func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_salary")
        )
        .where(Job.salary_min.isnot(None), Job.salary_max.isnot(None))
        .where(Job.salary_max <= 100000)  # 排除实习或异常岗位
        .group_by(Job.location_city)
    )
    result = db.execute(stmt).all()
    return {"average_salary_by_city": [{"city": r[0], "avg_salary": round(r[1], 2)} for r in result]}


@router.get("/top-cities")
def top_cities(db: Session = Depends(get_db)):
    """统计职位最多的前10个城市"""
    stmt = (
        select(Job.location_city, func.count(Job.id).label("count"))
        .group_by(Job.location_city)
        .order_by(func.count(Job.id).desc())
        .limit(10)
    )
    result = db.execute(stmt).all()
    return {"top_cities": [{"city": r[0], "count": r[1]} for r in result]}


@router.get("/skills")
def top_skills(db: Session = Depends(get_db)):
    """统计职位描述中最常出现的技能关键词"""
    # 取出所有职位描述
    descriptions = db.scalars(select(Job.description)).all()
    word_count = {}

    for desc in descriptions:
        if not desc:
            continue
        words = [w.strip().lower() for w in desc.replace(",", " ").split()]
        for w in words:
            if len(w) < 2 or len(w) > 20:
                continue
            word_count[w] = word_count.get(w, 0) + 1

    # 排名前10的关键词
    top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
    return {"top_skills": [{"skill": w, "count": c} for w, c in top_words]}
