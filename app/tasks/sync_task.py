"""
异步同步任务模块
使用独立线程执行同步，完全不阻塞主服务
"""

import os
import threading
from datetime import datetime
from loguru import logger
from app import create_app
from app.extensions import socketio, db
from app.models.watchlist import Watchlist
from app.services.stock_data_service import StockDataService
from app.services.alert_trigger_engine import alert_trigger_engine


def start_sync_task(task_id: str, start_date: str = None, end_date: str = None):
    """
    启动后台同步任务 - 使用独立线程

    Args:
        task_id: 任务ID
        start_date: 开始日期
        end_date: 结束日期
    """
    # 创建独立应用实例
    app = create_app(os.getenv("FLASK_ENV", "default"))

    def _sync_in_background():
        """在独立线程中执行同步"""
        results = []
        success_count = 0
        failed_count = 0

        try:
            with app.app_context():
                # 获取股票列表
                watchlist_items = Watchlist.query.all()

            # 串行同步每个股票（避免数据库锁）
            for item in watchlist_items:
                try:
                    # 同步数据
                    daily_result = StockDataService.sync_daily_data(
                        item.ts_code, start_date, end_date
                    )
                    basic_result = StockDataService.sync_daily_basic(
                        item.ts_code, start_date, end_date
                    )
                    moneyflow_result = StockDataService.sync_moneyflow(
                        item.ts_code, start_date, end_date
                    )

                    # 统计结果
                    success_types = []
                    total_added = 0

                    if daily_result['success']:
                        success_types.append(f"日线({daily_result.get('added', 0)}条)")
                        total_added += daily_result.get('added', 0)
                    if basic_result['success']:
                        success_types.append(f"指标({basic_result.get('added', 0)}条)")
                        total_added += basic_result.get('added', 0)
                    if moneyflow_result['success']:
                        success_types.append(f"资金({moneyflow_result.get('added', 0)}条)")
                        total_added += moneyflow_result.get('added', 0)

                    if success_types:
                        success_count += 1
                        results.append({
                            'ts_code': item.ts_code,
                            'name': item.name,
                            'success': True,
                            'added': total_added,
                            'details': ', '.join(success_types)
                        })
                    else:
                        failed_count += 1
                        results.append({
                            'ts_code': item.ts_code,
                            'name': item.name,
                            'success': False,
                            'message': '所有数据同步失败'
                        })

                except Exception as e:
                    failed_count += 1
                    results.append({
                        'ts_code': item.ts_code,
                        'name': item.name,
                        'success': False,
                        'message': str(e)
                    })

            # 更新同步时间
            with app.app_context():
                Watchlist.query.update({'last_sync': datetime.utcnow()})
                db.session.commit()

                # 触发预警
                try:
                    alert_result = alert_trigger_engine.run_alert_check()
                    logger.info(f"预警检查完成: {alert_result.get('message', '')}")
                except Exception as alert_error:
                    logger.error(f"预警检查失败: {str(alert_error)}")

                # 通知前端
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
            try:
                socketio.emit('sync_complete', {
                    'task_id': task_id,
                    'success': False,
                    'message': f'同步失败: {str(task_error)}'
                })
            except:
                pass

    # 使用独立线程执行，不阻塞主服务
    thread = threading.Thread(target=_sync_in_background, daemon=True)
    thread.start()
