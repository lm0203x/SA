"""
定时任务调度：每日 08:00 刷新自选股行情数据。
使用 SocketIO 背景任务 + eventlet sleep，避免阻塞主线程。
"""

from datetime import datetime, time, timedelta
from loguru import logger

from app.extensions import socketio, db
from app.models.watchlist import Watchlist
from app.services.stock_data_service import StockDataService


def _refresh_watchlist_quotes(days: int = 5):
    """
    刷新自选股近期行情/指标/资金流。
    默认抓取近 `days` 天，覆盖周末/漏数情况。
    """
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")

    watchlist = Watchlist.query.all()
    if not watchlist:
        logger.info("定时刷新：无自选股，跳过。")
        return

    success = 0
    for item in watchlist:
        try:
            StockDataService.sync_daily_data(item.ts_code, start_date, end_date)
            StockDataService.sync_daily_basic(item.ts_code, start_date, end_date)
            StockDataService.sync_moneyflow(item.ts_code, start_date, end_date)
            item.last_sync = datetime.utcnow()
            success += 1
        except Exception as e:
            logger.error(f"定时刷新 {item.ts_code} 失败: {e}")

    db.session.commit()
    logger.info(f"定时刷新完成，自选股 {success}/{len(watchlist)} 条已更新。")


def start_market_refresh_task(app):
    """
    启动每日 08:00 定时刷新任务。
    使用 socketio.start_background_task，在退出时无需额外清理。
    """

    def runner():
        with app.app_context():
            while True:
                now = datetime.now()
                target = datetime.combine(now.date(), time(hour=8, minute=0))
                if now >= target:
                    target += timedelta(days=1)
                wait_seconds = (target - now).total_seconds()
                socketio.sleep(wait_seconds)

                try:
                    _refresh_watchlist_quotes()
                except Exception as e:
                    logger.error(f"定时刷新任务执行失败: {e}")
                    db.session.rollback()
                # 小憩避免紧循环
                socketio.sleep(1)

    socketio.start_background_task(runner)
    logger.info("每日 08:00 行情定时刷新任务已启动。")
