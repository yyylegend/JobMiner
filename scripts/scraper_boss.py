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
def get_random_user_agent():
    """生成随机 User-Agent"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]
    return random.choice(user_agents)

def fetch_with_retry(url, headers, max_retries=3, backoff_factor=2.0):
    """带重试和指数退避的请求函数"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            # 每次请求使用随机 User-Agent
            current_headers = headers.copy()
            current_headers["User-Agent"] = get_random_user_agent()
            
            # 添加随机请求参数，避免缓存
            url_with_random = f"{url}&_t={int(time.time() * 1000)}"
            
            # 发送请求
            resp = requests.get(url_with_random, headers=current_headers, timeout=15)
            
            # 检查状态码
            if resp.status_code != 200:
                logger.warning(f"请求状态码异常: {resp.status_code}, URL: {url}")
                raise Exception(f"状态码异常: {resp.status_code}")
                
            # 解析 JSON
            data = resp.json()
            
            # 检查是否有数据
            job_list = data.get("zpData", {}).get("jobList", [])
            if not job_list:
                logger.warning(f"没有数据返回，可能被限流: {url}")
                raise Exception("空数据返回")
                
            return data
            
        except Exception as e:
            retry_count += 1
            wait_time = backoff_factor ** retry_count
            logger.warning(f"请求失败 ({retry_count}/{max_retries}): {e}, 等待 {wait_time:.1f} 秒后重试...")
            time.sleep(wait_time)
    
    # 所有重试都失败
    logger.error(f"达到最大重试次数 ({max_retries})，请求失败: {url}")
    return None

def fetch_boss_jobs(keywords=None, pages=2, max_retries=3):
    """通过官方 JSON 接口爬取 Boss直聘职位数据"""
    if keywords is None:
        keywords = ["数据分析", "Python", "算法工程师", "AI", "大数据"]

    # 基础请求头
    headers = {
        "Referer": "https://www.zhipin.com/web/geek/jobs",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cookie": "wt2=DvREW8OQwzxovjTbisVt-8d4wX4yVkjpVjQF0IAxW39Y0PVrSvbHZ-lB20NTuj2_raJCipZheGl-xo4I2stNnRg~~; wbg=0; zp_at=y5A7DnPSVcSDTXNGEQzmrh2jT_DTnzzbLv8SYQmIRaw~; lastCity=101020100; __zp_seo_uuid__=3e5612c8-1e3a-4544-a770-9ea5a4357b58"
    }

    jobs = []
    for kw in keywords:
        print(f"\n 正在抓取关键词: {kw}")
        logger.info(f"开始抓取关键词: {kw}")

        for page in range(1, pages + 1):
            url = f"https://www.zhipin.com/wapi/zpgeek/search/joblist.json?query={kw}&city=100010000&page={page}"
            print(f"第 {page} 页: {url}")
            logger.info(f"请求: {url}")

            # 使用重试机制发送请求
            data = fetch_with_retry(url, headers, max_retries=max_retries)
            if not data:
                continue  # 如果所有重试都失败，跳过此页

            job_list = data.get("zpData", {}).get("jobList", [])
            for job in job_list:
                jobs.append({
                    "title": job.get("jobName"),
                    "company": job.get("brandName"),
                    "salary": job.get("salaryDesc"),
                    "address": job.get("cityName"),
                    "description": job.get("jobLabels"),
                    "keyword": kw
                })

            # 使用更长的随机间隔，避免被检测
            sleep_time = random.uniform(3.0, 8.0)
            print(f"等待 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

    return jobs


# ================== 💾 数据写入 ==================
def _normalize_salary_text(s: str):
    s = s or ""
    s = s.strip()
    s = re.sub(r"\s+", "", s)
    s = s.replace("·", "")
    s = re.sub(r"\d{1,2}薪", "", s)
    return s

def _compute_salary_value(nums, s_norm: str, take: str):
    if not nums:
        return None
    num = float(nums[0] if take == "min" else nums[-1])
    s_lower = s_norm.lower()

    unit_factor = 1.0
    if "万" in s_norm:
        unit_factor = 10000.0
    elif "千" in s_norm or "k" in s_lower:
        unit_factor = 1000.0

    period_factor = 1.0
    if "年薪" in s_norm or "/年" in s_norm:
        period_factor = 1.0 / 12.0
    elif "元/天" in s_norm or "/天" in s_norm or "日薪" in s_norm or "每天" in s_norm or "元天" in s_norm:
        period_factor = 30.0
    elif "元/时" in s_norm or "元/小时" in s_norm or "/小时" in s_norm or "时薪" in s_norm:
        period_factor = 160.0

    value = num * unit_factor * period_factor
    return int(value)

def parse_salary_min(s: str):
    if not s or "面议" in s:
        return None
    s_norm = _normalize_salary_text(s)
    nums = re.findall(r"(\d+(?:\.\d+)?)", s_norm)
    return _compute_salary_value(nums, s_norm, take="min")

def parse_salary_max(s: str):
    if not s or "面议" in s:
        return None
    s_norm = _normalize_salary_text(s)
    nums = re.findall(r"(\d+(?:\.\d+)?)", s_norm)
    return _compute_salary_value(nums, s_norm, take="max")

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
        if s_max and s_max >= 100000:
            logger.warning(f"过滤异常薪资岗位：{j['title']} - {salary_text}")
            filtered += 1
            continue
        if s_min and s_min <= 500:
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
    
    # 添加命令行参数支持
    import sys
    keywords = ["大数据"]
    pages = 2
    max_retries = 3
    
    # 如果有命令行参数，则使用命令行参数
    if len(sys.argv) > 1:
        if "--keywords" in sys.argv:
            idx = sys.argv.index("--keywords")
            if idx + 1 < len(sys.argv):
                keywords = sys.argv[idx + 1].split(",")
                print(f"使用自定义关键词: {keywords}")
        
        if "--pages" in sys.argv:
            idx = sys.argv.index("--pages")
            if idx + 1 < len(sys.argv):
                pages = int(sys.argv[idx + 1])
                print(f"抓取页数: {pages}")
                
        if "--retries" in sys.argv:
            idx = sys.argv.index("--retries")
            if idx + 1 < len(sys.argv):
                max_retries = int(sys.argv[idx + 1])
                print(f"最大重试次数: {max_retries}")
    
    jobs = fetch_boss_jobs(keywords, pages=pages, max_retries=max_retries)
    print(f"共抓取 {len(jobs)} 条职位数据。")
    save_to_db(jobs)
    print("数据写入完成。")
    logger.info("任务完成")


if __name__ == "__main__":
    main()
