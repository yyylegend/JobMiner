from datetime import date
from app.db import SessionLocal
from app.models import Source, Company, Job

def main():
    db = SessionLocal()

    print("🚀 初始化数据库基础数据...")

    # 1️⃣ 检查并创建 Source
    source = db.query(Source).filter_by(name="Boss直聘").first()
    if not source:
        source = Source(name="Boss直聘", base_url="https://www.zhipin.com")
        db.add(source)
        db.commit()
        db.refresh(source)
        print("✅ 已创建 Source: Boss直聘")
    else:
        print("⚙️ Source 已存在:", source.name)

    # 2️⃣ 插入测试公司（若数据库为空）
    if not db.query(Company).first():
        c1 = Company(name="TapTap", location_city="Shanghai", location_country="CN")
        c2 = Company(name="Acme AI", location_city="Beijing", location_country="CN")
        db.add_all([c1, c2])
        db.commit()
        print("✅ 已插入示例公司数据。")
    else:
        print("⚙️ 公司数据已存在，跳过。")

    # 3️⃣ 插入测试职位（若数据库为空）
    if not db.query(Job).first():
        c1 = db.query(Company).filter_by(name="TapTap").first()
        c2 = db.query(Company).filter_by(name="Acme AI").first()

        j1 = Job(
            source_id=source.id,
            company_id=c1.id,
            title="Data Engineer",
            location_city="Shanghai",
            location_country="CN",
            remote="Onsite",
            salary_min=30000,
            salary_max=50000,
            currency="CNY",
            posted_at=date(2025, 10, 1),
            job_url="https://example.com/1",
            description="Python, SQL, Hive, Spark, Kafka"
        )
        j2 = Job(
            source_id=source.id,
            company_id=c2.id,
            title="ML Engineer",
            location_city="Beijing",
            location_country="CN",
            remote="Hybrid",
            salary_min=35000,
            salary_max=60000,
            currency="CNY",
            posted_at=date(2025, 9, 20),
            job_url="https://example.com/2",
            description="Python, PyTorch, Docker, Kubernetes"
        )
        db.add_all([j1, j2])
        db.commit()
        print("✅ 已插入示例职位数据。")
    else:
        print("⚙️ 职位表已有数据，跳过。")

    db.close()
    print("🎯 数据初始化完成。")


if __name__ == "__main__":
    main()
