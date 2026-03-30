"""
自选股API路由
"""

from flask import request, jsonify, current_app
from loguru import logger
from datetime import datetime
import uuid

from app.api import api_bp
from app.extensions import db, socketio
from app.models.watchlist import Watchlist
from app.models.stock_daily_history import StockDailyHistory
from app.services.tushare_service import TushareService
from app.services.stock_data_service import StockDataService
from app.services.alert_trigger_engine import alert_trigger_engine
from app.models.data_source_config import DataSourceConfig
from app.services.operation_log_service import OperationLogService
from app.utils.auth import get_request_user


@api_bp.route('/watchlist', methods=['GET'])
def get_watchlist():
    """获取自选股列表"""
    try:
        watchlist = Watchlist.query.order_by(Watchlist.added_at.desc()).all()

        watchlist_data = []
        for stock in watchlist:
            stock_data = stock.to_dict()
            latest_daily = StockDailyHistory.query.filter_by(ts_code=stock.ts_code).order_by(
                StockDailyHistory.trade_date.desc()
            ).first()
            stock_data['latest_close'] = float(latest_daily.close) if latest_daily and latest_daily.close is not None else None
            stock_data['latest_pct_chg'] = float(latest_daily.pct_chg) if latest_daily and latest_daily.pct_chg is not None else None
            stock_data['latest_trade_date'] = latest_daily.trade_date.isoformat() if latest_daily and latest_daily.trade_date else None
            watchlist_data.append(stock_data)

        OperationLogService.record(
            module='watchlist',
            action_type='view',
            action_name='查看自选股',
            user=get_request_user(),
            message=f'共返回 {len(watchlist)} 只自选股',
        )
        return jsonify({
            'success': True,
            'data': watchlist_data,
            'total': len(watchlist)
        })
    
    except Exception as e:
        logger.error(f"获取自选股列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/watchlist', methods=['POST'])
def add_to_watchlist():
    """添加自选股"""
    try:
        data = request.get_json()
        ts_code = data.get('ts_code')
        
        if not ts_code:
            return jsonify({
                'success': False,
                'message': '股票代码不能为空'
            }), 400
        
        # 检查是否已存在
        existing = Watchlist.query.filter_by(ts_code=ts_code).first()
        if existing:
            return jsonify({
                'success': False,
                'message': '该股票已在自选股中'
            }), 400
        
        # 从Tushare获取股票信息
        config = DataSourceConfig.query.filter_by(
            is_active=True,
            is_default=True,
            source_type='tushare'
        ).first()
        
        if config and config.config_data and 'token' in config.config_data:
            tushare_service = TushareService(config.config_data['token'])
            
            # 尝试获取股票基本信息
            try:
                stocks = tushare_service.get_stock_list()
                stock_info = next((s for s in stocks if s.get('ts_code') == ts_code), None)
                
                if stock_info:
                    watchlist_item = Watchlist(
                        ts_code=ts_code,
                        symbol=stock_info.get('symbol'),
                        name=stock_info.get('name'),
                        note=data.get('note', '')
                    )
                else:
                    # 如果找不到，使用用户提供的信息
                    watchlist_item = Watchlist(
                        ts_code=ts_code,
                        symbol=data.get('symbol', ts_code.split('.')[0]),
                        name=data.get('name', ts_code),
                        note=data.get('note', '')
                    )
            except Exception as e:
                logger.warning(f"从Tushare获取股票信息失败: {e}，使用用户输入")
                # 使用用户提供的信息
                watchlist_item = Watchlist(
                    ts_code=ts_code,
                    symbol=data.get('symbol', ts_code.split('.')[0]),
                    name=data.get('name', ts_code),
                    note=data.get('note', '')
                )
        else:
            # 没有配置数据源，使用用户输入
            watchlist_item = Watchlist(
                ts_code=ts_code,
                symbol=data.get('symbol', ts_code.split('.')[0]),
                name=data.get('name', ts_code),
                note=data.get('note', '')
            )
        
        db.session.add(watchlist_item)
        db.session.commit()
        
        logger.info(f"添加自选股成功: {ts_code}")
        OperationLogService.record(
            module='watchlist',
            action_type='create',
            action_name='添加自选股',
            user=get_request_user(),
            target_type='stock',
            target_id=watchlist_item.id,
            target_name=watchlist_item.ts_code,
            message='添加成功',
        )
        
        return jsonify({
            'success': True,
            'message': '添加成功',
            'data': watchlist_item.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加自选股失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/watchlist/<int:id>', methods=['DELETE'])
def remove_from_watchlist(id):
    """删除自选股"""
    try:
        watchlist_item = Watchlist.query.get(id)
        
        if not watchlist_item:
            return jsonify({
                'success': False,
                'message': '自选股不存在'
            }), 404
        
        ts_code = watchlist_item.ts_code
        db.session.delete(watchlist_item)
        db.session.commit()
        
        logger.info(f"删除自选股成功: {ts_code}")
        OperationLogService.record(
            module='watchlist',
            action_type='delete',
            action_name='删除自选股',
            user=get_request_user(),
            target_type='stock',
            target_id=id,
            target_name=ts_code,
            message='删除成功',
        )
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除自选股失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/watchlist/<int:id>', methods=['PUT'])
def update_watchlist(id):
    """更新自选股备注"""
    try:
        watchlist_item = Watchlist.query.get(id)
        
        if not watchlist_item:
            return jsonify({
                'success': False,
                'message': '自选股不存在'
            }), 404
        
        data = request.get_json()
        watchlist_item.note = data.get('note', watchlist_item.note)
        
        db.session.commit()
        OperationLogService.record(
            module='watchlist',
            action_type='update',
            action_name='更新自选股备注',
            user=get_request_user(),
            target_type='stock',
            target_id=watchlist_item.id,
            target_name=watchlist_item.ts_code,
            message='更新成功',
        )
        
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': watchlist_item.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新自选股失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/watchlist/<int:id>/sync', methods=['POST'])
def sync_watchlist_data(id):
    """同步单个自选股的数据"""
    try:
        watchlist_item = Watchlist.query.get(id)
        
        if not watchlist_item:
            return jsonify({
                'success': False,
                'message': '自选股不存在'
            }), 404
        
        ts_code = watchlist_item.ts_code
        
        # 获取日线数据参数
        data = request.get_json() if request.is_json else {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # 同步日线数据
        result = StockDataService.sync_daily_data(ts_code, start_date, end_date)
        
        if result['success']:
            # 更新最后同步时间
            watchlist_item.last_sync = datetime.utcnow()
            db.session.commit()
        OperationLogService.record(
            module='watchlist',
            action_type='sync',
            action_name='同步单只自选股',
            status='success' if result.get('success') else 'failed',
            user=get_request_user(),
            target_type='stock',
            target_id=watchlist_item.id,
            target_name=ts_code,
            message=result.get('message'),
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"同步自选股数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/watchlist/sync-all', methods=['POST'])
def sync_all_watchlist():
    """异步同步所有自选股的数据"""
    try:
        watchlist = Watchlist.query.all()

        if not watchlist:
            return jsonify({
                'success': False,
                'message': '自选股列表为空'
            }), 400

        data = request.get_json() if request.is_json else {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # 生成任务ID
        task_id = str(uuid.uuid4())

        # 立即返回任务提交成功
        from app.tasks.sync_task import start_sync_task
        start_sync_task(task_id, start_date, end_date)
        OperationLogService.record(
            module='watchlist',
            action_type='sync',
            action_name='同步全部自选股',
            user=get_request_user(),
            target_type='task',
            target_id=task_id,
            message='同步任务已提交',
        )

        return jsonify({
            'success': True,
            'message': '同步任务已提交',
            'task_id': task_id
        })

    except Exception as e:
        logger.error(f"提交同步任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/watchlist/<int:id>/push-config', methods=['PUT'])
def update_push_config(id):
    """更新自选股的推送配置"""
    try:
        watchlist_item = Watchlist.query.get(id)

        if not watchlist_item:
            return jsonify({
                'success': False,
                'message': '自选股不存在'
            }), 404

        data = request.get_json()

        # 更新推送开关
        if 'push_enabled' in data:
            watchlist_item.push_enabled = bool(data['push_enabled'])

        # 更新推送时间
        if 'push_time' in data:
            push_time_str = data['push_time']
            if push_time_str:
                # 解析 HH:MM 格式
                from datetime import time
                try:
                    hour, minute = map(int, push_time_str.split(':'))
                    watchlist_item.push_time = time(hour, minute)
                except:
                    return jsonify({
                        'success': False,
                        'message': '推送时间格式错误，请使用 HH:MM 格式'
                    }), 400
            else:
                watchlist_item.push_time = None

        db.session.commit()
        OperationLogService.record(
            module='watchlist',
            action_type='update',
            action_name='更新自选股推送配置',
            user=get_request_user(),
            target_type='stock',
            target_id=watchlist_item.id,
            target_name=watchlist_item.ts_code,
            message='推送配置更新成功',
            detail={
                'push_enabled': watchlist_item.push_enabled,
                'push_time': watchlist_item.push_time.strftime('%H:%M') if watchlist_item.push_time else None,
            },
        )

        return jsonify({
            'success': True,
            'message': '推送配置更新成功',
            'data': watchlist_item.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"更新推送配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
