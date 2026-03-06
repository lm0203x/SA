"""
异步同步任务模块
"""

from datetime import datetime
from loguru import logger
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
    from app import create_app
    import os

    app = create_app(os.getenv("FLASK_ENV", "default"))

    def _sync_all_task():
        """后台异步同步任务"""
        with app.app_context():
            success_count = 0
            failed_count = 0
            results = []

            try:
                # 重新查询数据库获取最新数据
                watchlist_items = Watchlist.query.all()

                for item in watchlist_items:
                    try:
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
                            success_count += 1
                            item.last_sync = datetime.utcnow()
                            results.append({
                                'ts_code': item.ts_code,
                                'name': item.name,
                                'success': True,
                                'added': total_added,
                                'details': ', '.join(success_types)
                            })
                        else:
                            failed_count += 1
                            error_messages = []
                            if not daily_result['success']:
                                error_messages.append(f"日线: {daily_result.get('message', '失败')}")
                            if not basic_result['success']:
                                error_messages.append(f"指标: {basic_result.get('message', '失败')}")
                            if not moneyflow_result['success']:
                                error_messages.append(f"资金流向: {moneyflow_result.get('message', '失败')}")

                            results.append({
                                'ts_code': item.ts_code,
                                'name': item.name,
                                'success': False,
                                'message': '; '.join(error_messages)
                            })

                    except Exception as e:
                        failed_count += 1
                        results.append({
                            'ts_code': item.ts_code,
                            'name': item.name,
                            'success': False,
                            'message': str(e)
                        })

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
                # 通知前端任务失败
                socketio.emit('sync_complete', {
                    'task_id': task_id,
                    'success': False,
                    'message': f'同步失败: {str(task_error)}'
                })

    # 启动后台任务
    socketio.start_background_task(_sync_all_task)
