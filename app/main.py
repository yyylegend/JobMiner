# app/main.py
from fastapi import FastAPI
from fastapi.routing import APIRoute
# 路由模块
from app.routers import home,jobs,skills,stats,dashboard,analytics
# ✅ 导入模型和数据库引擎（一定要在 create_all 前）
from app.models import Base
from app.db import engine

app = FastAPI(title="JobMiner API", version="0.1.0")

from fastapi.staticfiles import StaticFiles
import os

# 静态资源挂载
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ✅ 启动时建表（开发阶段用，后面我们会换成 Alembic）
Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health():
    return {"status": "ok"}

# 注册路由
app.include_router(jobs.router)
app.include_router(skills.router)
app.include_router(stats.router)
app.include_router(dashboard.router)
app.include_router(home.router)
app.include_router(analytics.router)

# 调试用：列出所有路由
@app.get("/__routes")
def list_routes():
    return [{"path": r.path, "name": r.name} for r in app.routes if isinstance(r, APIRoute)]
