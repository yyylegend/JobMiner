# 💼 JobMiner

一个个人学习项目，使用 FastAPI + SQLAlchemy + MySQL 构建的完整招聘数据分析系统。

## 项目简介

JobMiner 是一个用于学习数据工程与全栈开发的示例项目，
目标是通过实际构建一个 “岗位数据采集 + 清洗 + 分析 + API 服务” 系统，
完整打通从数据获取到可视化展示的流程。

系统目前具备以下核心能力：

🔍 数据采集：爬取 Boss 直聘（zhipin.com）的职位数据

🧹 数据清洗：自动过滤异常薪资（> 10 万/月 或 < 500 元/月）

💾 数据库存储：基于 SQLAlchemy ORM 的结构化建模

📊 数据分析接口：计算平均薪资、热门城市、常见技能词频

🌗 网页前端：带深浅色主题切换的简洁首页

🐳 Docker 支持：快速启动 MySQL + Adminer 数据库环境

## 技术栈
1. 后端框架FastAPI提供 RESTful API 与网页路由

2. ORM: SQLAlchemy	管理数据表和对象关系

3. 数据库:MySQL (Docker)	存储岗位信息、公司、数据源

4. 爬虫	Requests + BeautifulSoup	采集 Boss 直聘 JSON 接口

5. 前端	HTML + CSS	首页界面，带深浅色主题切换

6. 分析	SQL + Python	实现薪资与技能统计分析

## 运行步骤

1️⃣ 安装依赖
pip install -r requirements.txt

2️⃣ 启动 MySQL 与 Adminer（Docker）
docker compose up -d

访问数据库可视化界面：
http://localhost:8080

3️⃣ 创建数据库表
python -m scripts.create_tables

4️⃣ 运行爬虫脚本
python -m scripts.scraper_boss
脚本会自动抓取职位数据解析并清洗薪资写入数据库。

5️⃣ 启动 FastAPI 服务
uvicorn app.main:app --reload

访问：首页：http://127.0.0.1:8000 API 文档：http://127.0.0.1:8000/docs

## 示例接口输出

GET /api/analytics/salary/average
按城市统计平均薪资：

{
  "average_salary_by_city": [
    {"city": "北京", "avg_salary": 24350.5},
    {"city": "上海", "avg_salary": 22980.3}
  ]
}


GET /api/analytics/skills
职位描述中最常见的技能：

{
  "top_skills": [
    {"skill": "python", "count": 21},
    {"skill": "sql", "count": 17},
    {"skill": "excel", "count": 9}
  ]
}


## 未来计划

自动化定时爬虫（schedule / APScheduler）

前端可视化 Dashboard（Chart.js 或 ECharts）

多数据源支持（领英、智联、猎聘等）

机器学习分析（薪资预测、岗位聚类）


## 项目说明

本项目为个人学习用途，
主要用于练习全栈数据分析与工程化流程。

⚠️ 数据来源于公开网页，仅供学习与技术研究使用，
不用于商业用途，并遵守 Boss 直聘 robots.txt 及网站政策。

许可证
MIT License © 2025 Runqi Yang
自由使用、学习与修改，保留署名即可。
