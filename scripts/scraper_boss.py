import os
import time
import random
import logging
import requests
import re
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Job, Company, Source

# ================== 🔧 日志配置 ==================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ================== 🌐 爬虫核心 ==================
def fetch_boss_jobs(keywords=None, pages=2):
    """通过官方 JSON 接口爬取 Boss直聘职位数据"""
    if keywords is None:
        keywords = ["数据分析", "Python", "算法工程师", "AI", "大数据"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.zhipin.com/web/geek/jobs",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "wt2=DvREW8OQwzxovjTbisVt-8d4wX4yVkjpVjQF0IAxW39Y0PVrSvbHZ-lB20NTuj2_raJCipZheGl-xo4I2stNnRg~~; wbg=0; zp_at=y5A7DnPSVcSDTXNGEQzmrh2jT_DTnzzbLv8SYQmIRaw~; ab_guid=4ffc599d-2639-48e2-b220-228b99b9e595; AMP_8f1ede8e9c=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjIwY2NhMzc0Mi1hZDM0LTRhYTMtODQyZS1lZTNkN2VlYjI0NzUlMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjIyY2NkZTM0Yy1kMjM2LTQzNDYtYmE0Yy0wNTRjZDdmYTdmMTAlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzYxNTc4NTUxNjQyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlN0Q=; AMP_MKTG_8f1ede8e9c=JTdCJTdE; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1761574140,1761760976; HMACCOUNT=7890B99E63D9AD1B; lastCity=101020100; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1761783484; bst=V2R9olE-T10lxuVtRuyR8eKyO07DrXxS0~|R9olE-T10lxuVtRuyR8eKyO07DrWxCw~; AMP_8f1ede8e9c=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjIwY2NhMzc0Mi1hZDM0LTRhYTMtODQyZS1lZTNkN2VlYjI0NzUlMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjIyY2NkZTM0Yy1kMjM2LTQzNDYtYmE0Yy0wNTRjZDdmYTdmMTAlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzYxNTc4NTUxNjQyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc2MTc4NzM0NDAwMiU3RA==; __c=1761760973; __l=l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs%3Fcity%3D100010000%26query%3D%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590&r=&g=&s=3&friend_source=0&s=3&friend_source=0; __a=61329115.1761574139.1761574139.1761760973.22.2.12.22; SERVERID=606144fb348bc19e48aededaa626f54e|1761787373|1761760971; __zp_stoken__=7513fRkrDrsOAwpPDh0U3ERMeFhZFNUNKMktNRj5KSUlGSjhLS0ZKQClFNkPDhsOew7hFYsORFUQxSjg4REY4OElPIUpMxY%2FDhUVJPcORw4PDkcSOR2HDlRcpwrgcRcOGGxjDiTbDssOKM8K8w4Q0PMOgw4lFQ0dBwqDDgEPDgVHDhUXDjV%2FDjEDDi0NPQUA%2FR2VYZWFHT1RfYhFdYFBsa1ETV15cPUFFQ0bChMKoM0IdER8SGxYaCBkUHREfwo14FhoIGRQTHxEQFT5KwqrDgMKuxJjEmBvDv8SjwqTCoMKiwqvDtlXEjFPCtVzClXXDhHfDjFFawqjCoMONwq7CtsKhYW7CsmBdY8KAw4TDjsK6dGpbwrB2V8ODZnvDi3gfHAgaEUEbw67Cs8OW"
    }

    jobs = []
    for kw in keywords:
        print(f"\n 正在抓取关键词: {kw}")
        logger.info(f"开始抓取关键词: {kw}")

        for page in range(1, pages + 1):
            url = f"https://www.zhipin.com/wapi/zpgeek/search/joblist.json?query={kw}&city=100010000&page={page}"
            print(f"第 {page} 页: {url}")
            logger.info(f"请求: {url}")

            try:
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()
            except Exception as e:
                logger.error(f"请求或解析失败: {e}")
                continue

            job_list = data.get("zpData", {}).get("jobList", [])
            if not job_list:
                logger.warning(f"没有数据返回，可能被限流: {url}")
                continue

            for job in job_list:
                jobs.append({
                    "title": job.get("jobName"),
                    "company": job.get("brandName"),
                    "salary": job.get("salaryDesc"),
                    "address": job.get("cityName"),
                    "description": job.get("jobLabels"),
                    "keyword": kw
                })

            time.sleep(random.uniform(1.5, 3.0))  # 防止访问过快被封

    return jobs


# ================== 💾 数据写入 ==================
def parse_salary_min(s: str):
    if not s or "面议" in s:
        return None
    s = s.replace(" ", "")
    # 提取数字区间
    m = re.findall(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return None
    num = float(m[0])

    # 判断单位
    if "千" in s:
        num *= 1000
    elif "万" in s:
        num *= 10000
    elif "元/天" in s or "元天" in s:
        num *= 30  # 估算成月薪
    elif "年" in s:
        num /= 12  # 年薪转月薪

    return int(num)

def parse_salary_max(s: str):
    if not s or "面议" in s:
        return None
    s = s.replace(" ", "")
    m = re.findall(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return None
    num = float(m[-1])

    if "千" in s:
        num *= 1000
    elif "万" in s:
        num *= 10000
    elif "元/天" in s or "元天" in s:
        num *= 30
    elif "年" in s:
        num /= 12

    return int(num)

def save_to_db(jobs):
    db: Session = SessionLocal()

    # 查找或创建数据源
    source = db.scalar(select(Source).where(Source.name == "Boss直聘JSON"))
    if not source:
        source = Source(name="Boss直聘JSON", base_url="https://www.zhipin.com")
        db.add(source)
        db.commit()
        db.refresh(source)
        logger.info("已创建 Source: Boss直聘JSON")

    added, skipped, filtered = 0, 0, 0

    for j in jobs:
        # ========== 🏢 公司表处理 ==========
        company_obj = db.scalar(select(Company).where(Company.name == j["company"]))
        if not company_obj:
            company_obj = Company(name=j["company"], location_city=j.get("address"))
            db.add(company_obj)
            db.commit()
            db.refresh(company_obj)

        # ========== 💰 薪资解析与过滤 ==========
        salary_text = j.get("salary")
        s_min = parse_salary_min(salary_text)
        s_max = parse_salary_max(salary_text)

        # 过滤异常薪资（>100000 或 <500）
        if s_max and s_max > 100000:
            logger.warning(f"过滤异常薪资岗位：{j['title']} - {salary_text}")
            filtered += 1
            continue
        if s_min and s_min < 500:
            logger.warning(f"过滤异常低薪岗位：{j['title']} - {salary_text}")
            filtered += 1
            continue

        # ========== 🔍 去重判断 ==========
        exists = db.scalar(
            select(Job).where(
                Job.title == j["title"],
                Job.company_id == company_obj.id,
                Job.source_id == source.id
            )
        )
        if exists:
            skipped += 1
            continue

        # ========== ✅ 插入新岗位 ==========
        job = Job(
            source_id=source.id,
            company_id=company_obj.id,
            title=j.get("title"),
            location_city=j.get("address"),
            description=", ".join(j.get("description") or []),
            salary_min=s_min,
            salary_max=s_max,
            currency="CNY",
            posted_at=datetime.now().date(),
            created_at=datetime.now(),
        )
        db.add(job)
        added += 1

    db.commit()
    db.close()
    print(f"✅ 已插入 {added} 条新职位，跳过 {skipped} 条重复，过滤 {filtered} 条异常。")
    logger.info(f"插入 {added} 条新职位，跳过 {skipped} 条重复，过滤 {filtered} 条异常。")

# ================== 🚀 主函数 ==================
def main():
    print("[JobMiner] 开始抓取 Boss直聘 JSON 接口数据...")
    logger.info("启动 JSON 爬虫任务")
    jobs = fetch_boss_jobs(["数据分析", "Python"], pages=2)
    print(f"共抓取 {len(jobs)} 条职位数据。")
    save_to_db(jobs)
    print("数据写入完成。")
    logger.info("任务完成")


if __name__ == "__main__":
    main()
