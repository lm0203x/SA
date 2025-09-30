"""
自选股API路由
"""

from flask import request, jsonify
from loguru import logger
from datetime import datetime

from app.api import api_bp
from app.extensions import db
from app.models.watchlist import Watchlist
from app.services.tushare_service import TushareService
from app.services.stock_data_service import StockDataService
from app.models.data_source_config import DataSourceConfig


@api_bp.route('/watchlist', methods=['GET'])
def get_watchlist():
    """获取自选股列表"""
    try:
        watchlist = Watchlist.query.order_by(Watchlist.added_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [stock.to_dict() for stock in watchlist],
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
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"同步自选股数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/watchlist/sync-all', methods=['POST'])
def sync_all_watchlist():
    """同步所有自选股的数据"""
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
        
        success_count = 0
        failed_count = 0
        results = []
        
        for item in watchlist:
            try:
                result = StockDataService.sync_daily_data(
                    item.ts_code, 
                    start_date, 
                    end_date
                )
                
                if result['success']:
                    success_count += 1
                    item.last_sync = datetime.utcnow()
                    results.append({
                        'ts_code': item.ts_code,
                        'name': item.name,
                        'success': True,
                        'added': result.get('added', 0)
                    })
                else:
                    failed_count += 1
                    results.append({
                        'ts_code': item.ts_code,
                        'name': item.name,
                        'success': False,
                        'message': result.get('message', '未知错误')
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
        
        return jsonify({
            'success': True,
            'message': f'同步完成: 成功{success_count}只, 失败{failed_count}只',
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results
        })
    
    except Exception as e:
        logger.error(f"批量同步失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
