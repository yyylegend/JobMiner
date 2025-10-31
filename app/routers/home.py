# app/routers/home.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["Home"])

# 绑定模板目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """渲染主页 HTML"""
    return templates.TemplateResponse("home.html", {"request": request})