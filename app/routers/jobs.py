# ============================================================
#  📂 文件说明：app/routers/jobs.py
#  本文件是 JobMiner 项目的“职位信息接口”模块。
#  功能：定义 /api/jobs 路由，实现岗位列表查询、筛选、分页。
# ============================================================

# ---- 导入 FastAPI 所需工具 ----
from fastapi import APIRouter, Query  # APIRouter 用于模块化路由，Query 用于定义查询参数
from typing import Optional, List
from datetime import date

# ---- 创建一个 APIRouter 实例 ----
# prefix 表示该模块下的所有接口都以 /api/jobs 开头
# tags 会在 Swagger 文档中显示分类标题
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# ---- 模拟数据（先用 Python 列表代替数据库）----
# 后续我们会替换为 MySQL 数据库。
# 每个职位是一个字典，包含常见字段，如 title、company、city、salary 等。
JOBS = [
    {
        "id": 1,
        "title": "Data Engineer",
        "company": "TapTap",
        "city": "Shanghai",
        "country": "CN",
        "remote": "Onsite",       # 现场办公
        "salary_min": 30000,
        "salary_max": 50000,
        "currency": "CNY",
        "posted_at": date(2025, 10, 1),
        "url": "https://example.com/1",
        "skills": ["python", "sql", "spark", "hive", "kafka"],
    },
    {
        "id": 2,
        "title": "ML Engineer",
        "company": "Acme AI",
        "city": "Beijing",
        "country": "CN",
        "remote": "Hybrid",       # 混合办公
        "salary_min": 35000,
        "salary_max": 60000,
        "currency": "CNY",
        "posted_at": date(2025, 9, 20),
        "url": "https://example.com/2",
        "skills": ["python", "pytorch", "docker", "k8s"],
    },
    {
        "id": 3,
        "title": "Backend Engineer (Python)",
        "company": "FooTech",
        "city": "Remote",
        "country": "CN",
        "remote": "Remote",       # 全远程
        "salary_min": 26000,
        "salary_max": 42000,
        "currency": "CNY",
        "posted_at": date(2025, 9, 28),
        "url": "https://example.com/3",
        "skills": ["python", "flask", "mysql", "redis"],
    },
]


# ============================================================
# 🧩 定义接口函数：GET /api/jobs
# 功能：返回职位列表，并支持条件筛选（关键词、城市、远程类型）+ 分页。
# ============================================================
@router.get("/")  # 当访问 /api/jobs 时触发此函数
async def list_jobs(
    # 下面这些是“查询参数”（即 URL 参数，如 /api/jobs?q=engineer）
    q: Optional[str] = Query(None, description="按标题关键词模糊匹配"),
    city: Optional[str] = Query(None, description="城市（大小写不敏感）"),
    remote: Optional[str] = Query(
        None,
        regex="^(Onsite|Hybrid|Remote)$",
        description="办公方式，可选值：Onsite、Hybrid、Remote",
    ),
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    size: int = Query(10, ge=1, le=100, description="每页数量，默认10，最大100"),
):
    """
    这个接口会根据用户输入的查询条件，从 JOBS 列表中筛选出符合条件的职位，
    然后返回分页结果。
    """

    # ---- 第一步：准备初始数据 ----
    data = JOBS  # 在后端项目中，这通常会是数据库查询结果

    # ---- 第二步：按关键词过滤 ----
    if q:  # 如果用户输入了 q 参数
        q_lower = q.lower()
        # 使用 Python 列表推导式过滤
        data = [job for job in data if q_lower in job["title"].lower()]

    # ---- 第三步：按城市过滤 ----
    if city:
        data = [job for job in data if (job["city"] or "").lower() == city.lower()]

    # ---- 第四步：按远程类型过滤 ----
    if remote:
        data = [job for job in data if job["remote"] == remote]

    # ---- 第五步：排序（按发布时间从新到旧）----
    # key=lambda j: j.get("posted_at") 表示按日期排序
    data = sorted(data, key=lambda j: j.get("posted_at") or date.min, reverse=True)

    # ---- 第六步：分页处理 ----
    start = (page - 1) * size
    end = start + size
    items = data[start:end]

    # ---- 第七步：返回结果 ----
    return {
        "total": len(data),  # 符合条件的总数量
        "page": page,
        "size": size,
        "items": items,      # 当前页的数据
    }

# ============================================================
# ✅ 访问测试：
# http://127.0.0.1:8000/api/jobs                → 所有岗位
# http://127.0.0.1:8000/api/jobs?q=engineer    → 模糊搜索标题
# http://127.0.0.1:8000/api/jobs?city=Shanghai → 筛选城市
# http://127.0.0.1:8000/api/jobs?remote=Remote → 远程岗位
# http://127.0.0.1:8000/api/jobs?page=1&size=2 → 分页
# ============================================================
