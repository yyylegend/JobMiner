from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from datetime import datetime
from scripts.scraper_boss import main as boss_spider


def run_spider():
    """执行爬虫任务"""
    print(f"\n🕒 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 启动定时任务：Boss直聘爬虫")
    try:
        asyncio.run(boss_spider())
    except Exception as e:
        print(f"❌ 爬虫执行失败：{e}")


def start_scheduler():
    """启动定时调度器"""
    scheduler = BackgroundScheduler()

    # ✅ 每天上午 10:00 自动运行一次
    scheduler.add_job(run_spider, "cron", hour=10, minute=0, id="daily_boss_job")

    # 🧩 可选：每隔 6 小时运行一次（测试阶段建议启用）
    # scheduler.add_job(run_spider, "interval", hours=6, id="test_interval")

    scheduler.start()
    print("✅ 调度器已启动。任务将在每天 10:00 自动运行。")
    print("💡 保持程序运行中以维持后台任务执行（Ctrl+C 退出）")

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\n🛑 调度器已关闭。")


if __name__ == "__main__":
    start_scheduler()