from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.jobs.daily_predictions import run_daily_predictions
from app.jobs.send_telegram import send_today_predictions
from app.jobs.resolve_predictions import resolve_predictions

scheduler = AsyncIOScheduler(timezone=settings.timezone)


def start_scheduler() -> None:
    scheduler.add_job(run_daily_predictions, CronTrigger(hour=8, minute=0), id="daily_predictions", replace_existing=True)
    scheduler.add_job(send_today_predictions, CronTrigger(hour=8, minute=5), id="send_telegram", replace_existing=True)
    scheduler.add_job(resolve_predictions, CronTrigger(hour=1, minute=30), id="resolve_predictions", replace_existing=True)
    scheduler.start()
