# app/routers/dashboard.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from collections import Counter
import re
from app.db import SessionLocal
from app.models import Job

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(request: Request):
    """
    渲染 JobMiner 数据分析仪表盘页面
    """
    db = SessionLocal()
    try:
        # 1️⃣ 技能统计
        results = db.execute(select(Job.description)).scalars().all()
        keywords = ["Python", "SQL", "Spark", "Kafka", "Docker", "Kubernetes", "TensorFlow", "PyTorch"]
        counter = Counter()

        for desc in results:
            if not desc:
                continue
            for kw in keywords:
                if re.search(rf"\b{kw}\b", desc, re.IGNORECASE):
                    counter[kw] += 1

        top_skills = counter.most_common(10)

        # 2️⃣ 城市薪资统计
        stmt = (
            select(
                Job.location_city.label("city"),
                func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_salary")
            )
            .where(Job.salary_min.isnot(None))
            .group_by(Job.location_city)
        )
        salary_data = db.execute(stmt).all()

        cities = [r.city for r in salary_data if r.city]
        avg_salaries = [float(r.avg_salary) for r in salary_data if r.avg_salary]

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "skills": top_skills,
                "cities": cities,
                "avg_salaries": avg_salaries,
            },
        )

    finally:
        db.close()
