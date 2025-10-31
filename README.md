# 💼 JobMiner

> A personal learning project by **Runqi Yang** — building a full-stack job analytics system using **FastAPI**, **SQLAlchemy**, and **MySQL**.

---

## 🧠 Overview

**JobMiner** is a personal learning project that demonstrates a complete data pipeline for job data analytics.  
It scrapes job postings from **Boss直聘 (zhipin.com)**, stores them into a **MySQL** database using **SQLAlchemy ORM**,  
and exposes RESTful APIs via **FastAPI** for data visualization and analysis.

This project focuses on:
- 🔍 Web scraping and data cleaning
- 💾 Database modeling with SQLAlchemy
- 📊 Analytics API development
- 🌐 Frontend integration (FastAPI + HTML/CSS)
- ⚙️ Docker-based development workflow

---

## 🏗️ Project Structure


JobMiner/
│
├── app/
│ ├── main.py # FastAPI entry point
│ ├── db.py # Database connection and Base
│ ├── models.py # ORM models (Source, Company, Job)
│ ├── routes/
│ │ ├── jobs.py # Job APIs
│ │ └── analytics.py # Analytics APIs (salary, skills, cities)
│ ├── templates/
│ │ └── home.html # Main web page
│ └── static/
│ └── styles.css # Frontend styling
│
├── scripts/
│ ├── scraper_boss.py # Boss直聘 data scraper
│ ├── create_tables.py # Database table creation
│ └── seed_mysql.py # Optional: test data generator
│
├── docker-compose.yml # MySQL + Adminer containers
├── .env # DB credentials (not committed)
├── .gitignore
├── README.md
└── requirements.txt


---

## ⚙️ Tech Stack

| Layer | Technology | Description |
|-------|-------------|-------------|
| Backend | **FastAPI** | RESTful API framework |
| ORM | **SQLAlchemy 2.x** | Object-relational mapping |
| Database | **MySQL (Docker)** | Persistent job storage |
| Scraper | **Requests + BeautifulSoup** | Crawl Boss直聘 JSON API |
| Frontend | **HTML + CSS** | Minimal homepage with dark/light mode |
| Analytics | **SQL + Python** | Salary, skill, and city statistics |

---

## 🧩 Key Features

- 🚀 **Real-time Job Scraping** — Crawls Boss直聘 JSON API for jobs like “数据分析”, “Python”, “AI”.
- 💾 **Clean Database Schema** — Stores job, company, and source tables with proper relationships.
- 🧹 **Data Cleaning** — Filters abnormal salaries (e.g., >100,000 or <500).
- 📈 **Analytics API** — Provides endpoints for:
  - `/api/analytics/salary/average` → average salary by city  
  - `/api/analytics/top-cities` → most active job locations  
  - `/api/analytics/skills` → most frequent skill keywords
- 🌗 **Light/Dark Theme Frontend** — PHP-style homepage built with HTML/CSS.
- 🐳 **Dockerized Database** — MySQL + Adminer for quick visualization and management.

---

## 🧰 Setup & Run

### 1️⃣ Clone and install dependencies
```bash
git clone https://github.com/<your-username>/JobMiner.git
cd JobMiner
pip install -r requirements.txt

2️⃣ Start MySQL and Adminer (Docker)
docker compose up -d


Access Adminer at → http://localhost:8080

3️⃣ Initialize database tables
python -m scripts.create_tables

4️⃣ Run the scraper
python -m scripts.scraper_boss

5️⃣ Start FastAPI server
uvicorn app.main:app --reload


Visit:

API Docs → http://127.0.0.1:8000/docs

Homepage → http://127.0.0.1:8000

🧮 Example API Output

GET /api/analytics/salary/average

{
  "average_salary_by_city": [
    {"city": "北京", "avg_salary": 24350.5},
    {"city": "上海", "avg_salary": 22980.3}
  ]
}


GET /api/analytics/skills

{
  "top_skills": [
    {"skill": "python", "count": 21},
    {"skill": "sql", "count": 17},
    {"skill": "excel", "count": 9}
  ]
}

🧠 Future Improvements

🕒 Automated daily scraping (scheduler)

📊 Frontend dashboard using Chart.js or ECharts

🌍 Multi-source integration (LinkedIn, 智联招聘)

💡 ML-based salary prediction or job classification

📚 Learning Purpose

This project was built purely for learning and portfolio demonstration.
It is not intended for commercial use, and respects Boss直聘’s robots.txt and data policies.

🧩 Goal: Practice full-stack data engineering — from scraping → database → API → analytics.

📄 License

MIT License © 2025 Runqi Yang
