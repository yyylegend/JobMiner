# app/routers/dashboard.py
from fastapi import APIRouter, Response
from sqlalchemy import func, select
from app.db import SessionLocal
from app.models import Job
from collections import Counter
import re
import json

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard", response_class=Response)
def dashboard_page():
    """
    返回一个可视化仪表盘页面（HTML + Chart.js）
    """

    db = SessionLocal()
    try:
        # 1️⃣ 读取职位描述并统计技能出现频率
        results = db.execute(select(Job.description)).scalars().all()
        skills = [
            "Python", "SQL", "Spark", "Kafka", "Docker", "Kubernetes", "PyTorch", "TensorFlow"
        ]
        counter = Counter()
        for desc in results:
            if not desc:
                continue
            for s in skills:
                if re.search(rf"\b{s}\b", desc, re.IGNORECASE):
                    counter[s] += 1

        top_skills = counter.most_common(10)
        skill_labels = [s for s, _ in top_skills]
        skill_counts = [c for _, c in top_skills]

        # 2️⃣ 统计城市平均薪资
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
        salaries = [float(r.avg_salary) for r in salary_data if r.avg_salary]

        # 3️⃣ 生成 HTML 页面（Chart.js）
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>JobMiner Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f7fa;
                    margin: 0;
                    padding: 20px;
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                }}
                .chart-container {{
                    width: 80%;
                    margin: 30px auto;
                    background: white;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                canvas {{
                    width: 100% !important;
                    height: 400px !important;
                }}
            </style>
        </head>
        <body>
            <h1>📊 JobMiner Dashboard</h1>
            <div class="chart-container">
                <h2>🔥 Top Skills Demand</h2>
                <canvas id="skillsChart"></canvas>
            </div>
            <div class="chart-container">
                <h2>💰 Average Salary by City</h2>
                <canvas id="salaryChart"></canvas>
            </div>

            <script>
                // 技能数据
                const skillLabels = {json.dumps(skill_labels)};
                const skillCounts = {json.dumps(skill_counts)};
                const ctx1 = document.getElementById('skillsChart').getContext('2d');
                new Chart(ctx1, {{
                    type: 'bar',
                    data: {{
                        labels: skillLabels,
                        datasets: [{{
                            label: 'Skill Frequency',
                            data: skillCounts,
                            backgroundColor: 'rgba(75, 192, 192, 0.6)'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{ display: false }},
                            title: {{ display: true, text: 'Top 10 Skills' }}
                        }}
                    }}
                }});

                // 薪资数据
                const cityLabels = {json.dumps(cities)};
                const citySalaries = {json.dumps(salaries)};
                const ctx2 = document.getElementById('salaryChart').getContext('2d');
                new Chart(ctx2, {{
                    type: 'bar',
                    data: {{
                        labels: cityLabels,
                        datasets: [{{
                            label: 'Average Salary (CNY)',
                            data: citySalaries,
                            backgroundColor: 'rgba(255, 159, 64, 0.6)'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{ display: false }},
                            title: {{ display: true, text: 'Average Salary by City' }}
                        }},
                        scales: {{
                            y: {{ beginAtZero: true }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """

        return Response(content=html, media_type="text/html")

    finally:
        db.close()
