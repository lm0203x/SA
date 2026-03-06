"""
异步同步任务模块
"""

import os
import eventlet
from datetime import datetime
from loguru import logger
from app import create_app
from app.extensions import socketio, db
from app.models.watchlist import Watchlist
from app.services.stock_data_service import StockDataService
from app.services.alert_trigger_engine import alert_trigger_engine


def start_sync_task(task_id: str, start_date: str = None, end_date: str = None):
    """
    启动后台同步任务

    Args:
        task_id: 任务ID
        start_date: 开始日期
        end_date: 结束日期
    """
    # 创建独立的应用实例，避免阻塞主应用
    app = create_app(os.getenv("FLASK_ENV", "default"))

    def _sync_all_task():
        """后台异步同步任务"""
        # 使用 eventlet 的池来并行执行网络请求
        pool = eventlet.GreenPool()

        # 用于存储结果的共享变量
        results = []

        with app.app_context():
            try:
                # 重新查询数据库获取最新数据
                watchlist_items = Watchlist.query.all()

                # 使用 greenlet 并行同步，每个股票一个协程
                greenlets = []
                for item in watchlist_items:
                    greenlet = pool.spawn(_sync_single_stock, item, start_date, end_date)
                    greenlets.append(greenlet)

                # 等待所有任务完成
                for greenlet in greenlets:
                    try:
                        result = greenlet.wait()
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.error(f"同步任务等待失败: {str(e)}")

                # 统计结果
                success_count = sum(1 for r in results if r.get('success'))
                failed_count = len(results) - success_count

                # 更新最后同步时间
                Watchlist.query.update({'last_sync': datetime.utcnow()})
                db.session.commit()

                # 同步完成后触发预警检查
                try:
                    alert_result = alert_trigger_engine.run_alert_check()
                    logger.info(f"同步完成后预警检查完成: {alert_result.get('message', '')}")
                except Exception as alert_error:
                    logger.error(f"同步后预警检查失败: {str(alert_error)}")

                # 通知前端同步完成
                socketio.emit('sync_complete', {
                    'task_id': task_id,
                    'success': True,
                    'message': f'同步完成: 成功{success_count}只, 失败{failed_count}只',
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'results': results
                })

            except Exception as task_error:
                logger.error(f"后台同步任务失败: {str(task_error)}")
                db.session.rollback()
                # 通知前端任务失败
                socketio.emit('sync_complete', {
                    'task_id': task_id,
                    'success': False,
                    'message': f'同步失败: {str(task_error)}'
                })

    # 启动后台任务
    socketio.start_background_task(_sync_all_task)


def _sync_single_stock(item, start_date, end_date):
    """同步单个股票数据"""
    try:
        # 使用 eventlet.sleep 让出控制权，避免阻塞
        eventlet.sleep(0)

        # 同步三种数据：日线行情、每日指标、资金流向
        daily_result = StockDataService.sync_daily_data(
            item.ts_code,
            start_date,
            end_date
        )

        basic_result = StockDataService.sync_daily_basic(
            item.ts_code,
            start_date,
            end_date
        )

        moneyflow_result = StockDataService.sync_moneyflow(
            item.ts_code,
            start_date,
            end_date
        )

        # 统计成功的数据类型
        success_types = []
        total_added = 0

        if daily_result['success']:
            success_types.append(f"日线({daily_result.get('added', 0)}条)")
            total_added += daily_result.get('added', 0)

        if basic_result['success']:
            success_types.append(f"指标({basic_result.get('added', 0)}条)")
            total_added += basic_result.get('added', 0)

        if moneyflow_result['success']:
            success_types.append(f"资金流向({moneyflow_result.get('added', 0)}条)")
            total_added += moneyflow_result.get('added', 0)

        if success_types:
            return {
                'ts_code': item.ts_code,
                'name': item.name,
                'success': True,
                'added': total_added,
                'details': ', '.join(success_types)
            }
        else:
            error_messages = []
            if not daily_result['success']:
                error_messages.append(f"日线: {daily_result.get('message', '失败')}")
            if not basic_result['success']:
                error_messages.append(f"指标: {basic_result.get('message', '失败')}")
            if not moneyflow_result['success']:
                error_messages.append(f"资金流向: {moneyflow_result.get('message', '失败')}")

            return {
                'ts_code': item.ts_code,
                'name': item.name,
                'success': False,
                'message': '; '.join(error_messages)
            }

    except Exception as e:
        return {
            'ts_code': item.ts_code,
            'name': item.name,
            'success': False,
            'message': str(e)
        }
