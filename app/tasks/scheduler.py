"""
定时任务调度：
1. 每日 08:00 刷新自选股行情数据
2. 每分钟检查自选股推送任务
使用 SocketIO 背景任务 + eventlet sleep，避免阻塞主线程。
"""

from datetime import datetime, time, timedelta
from loguru import logger

from app.extensions import socketio, db
from app.models.watchlist import Watchlist
from app.services.stock_data_service import StockDataService
from app.services.alert_trigger_engine import alert_trigger_engine
from app.services.analysis_push_service import AnalysisPushService


def _last_trading_day() -> str:
    """返回最近一个交易日(简单以工作日近似)。"""
    day = datetime.now().date() - timedelta(days=1)
    while day.weekday() >= 5:  # 5=周六 6=周日
        day -= timedelta(days=1)
    return day.strftime("%Y%m%d")


def _refresh_watchlist_quotes():
    """
    每日刷新自选股的前一交易日行情/指标/资金流，并触发预警。
    """
    trade_date = _last_trading_day()

    watchlist = Watchlist.query.all()
    if not watchlist:
        logger.info("定时刷新：无自选股，跳过。")
        return

    success = 0
    for item in watchlist:
        try:
            StockDataService.sync_daily_data(item.ts_code, start_date=trade_date, end_date=trade_date)
            StockDataService.sync_daily_basic(item.ts_code, start_date=trade_date, end_date=trade_date)
            StockDataService.sync_moneyflow(item.ts_code, start_date=trade_date, end_date=trade_date)
            item.last_sync = datetime.utcnow()
            success += 1
        except Exception as e:
            logger.error(f"定时刷新 {item.ts_code} 失败: {e}")

    db.session.commit()
    logger.info(f"定时刷新完成，自选股 {success}/{len(watchlist)} 条已更新。")

    # 刷新后立即跑一次预警检查，触发Webhook
    try:
        result = alert_trigger_engine.run_alert_check()
        if not result.get("success", False):
            logger.error(f"定时刷新后预警检查失败: {result.get('message')}")
    except Exception as e:
        logger.error(f"定时刷新后预警检查异常: {e}")


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


def _check_and_push_analysis():
    """
    检查并执行自选股定时推送
    每分钟检查一次，开启推送且到达推送时间的股票执行 AI 分析推送
    """
    logger.info("[定时推送检查] 开始检查...")

    now = datetime.now()
    current_time = now.time()
    current_date = now.date()

    # 强制关闭当前 session，强制从数据库重新获取
    db.session.close()
    db.session.remove()

    # 获取需要推送的自选股（重新查询）
    watchlist = Watchlist.query.filter_by(push_enabled=True).all()

    logger.info(f"[定时推送检查] 当前开启推送的自选股数量: {len(watchlist)}")

    if not watchlist:
        return

    for item in watchlist:
        try:
            # 检查是否到达推送时间
            if item.push_time:
                # 比较时间（忽略日期）
                push_time = item.push_time
                logger.info(f"[定时推送检查] {item.ts_code} 推送时间: {push_time}, 当前时间: {current_time}")

                # 检查今天是否已经推送过
                if item.last_push_at:
                    last_date = item.last_push_at.date()
                    if last_date == current_date:
                        logger.info(f"[定时推送检查] 今日已推送，跳过: {item.ts_code}")
                        continue

                # 判断当前时间是否已经超过推送时间
                if current_time > push_time:
                    # 执行推送
                    logger.info(f"[定时推送] 执行推送: {item.ts_code} {item.name}")
                    AnalysisPushService.push_analysis(item)
                else:
                    logger.info(f"[定时推送检查] 未到推送时间，跳过: {item.ts_code}")

        except Exception as e:
            logger.error(f"定时推送处理 {item.ts_code} 失败: {e}")


def start_analysis_push_task(app):
    """
    启动定时推送检查任务
    每分钟检查一次是否有需要推送的自选股
    """

    def runner():
        with app.app_context():
            while True:
                # 每 60 秒检查一次
                socketio.sleep(60)

                try:
                    _check_and_push_analysis()
                except Exception as e:
                    logger.error(f"定时推送检查任务执行失败: {e}")

    socketio.start_background_task(runner)
    logger.info("自选股 AI 分析定时推送任务已启动（每分钟检查）")
