"""
股票数据API路由
提供股票实时数据、历史数据等接口
"""

from flask import request, jsonify
from loguru import logger
from app.api import api_bp
from app.models.data_source_config import DataSourceConfig
from app.services.tushare_service import TushareService


@api_bp.route('/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表"""
    try:
        # 获取激活的数据源
        config = DataSourceConfig.query.filter_by(
            is_active=True,
            is_default=True
        ).first()
        
        if not config:
            return jsonify({
                'success': False,
                'message': '没有激活的数据源，请先配置数据源'
            }), 400
        
        # 根据数据源类型获取数据
        if config.source_type == 'tushare':
            token = config.config_data.get('token')
            if not token:
                return jsonify({
                    'success': False,
                    'message': 'Tushare Token未配置'
                }), 400
            
            tushare_service = TushareService(token)
            stocks = tushare_service.get_stock_list()
            
            return jsonify({
                'success': True,
                'data': stocks,
                'total': len(stocks),
                'source': 'tushare'
            })
        
        else:
            return jsonify({
                'success': False,
                'message': f'暂不支持的数据源: {config.source_type}'
            }), 400
    
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/stocks/realtime', methods=['POST'])
def get_realtime_quotes():
    """获取实时行情"""
    try:
        data = request.get_json()
        ts_codes = data.get('symbols', [])
        
        if not ts_codes:
            return jsonify({
                'success': False,
                'message': '请提供股票代码列表'
            }), 400
        
        # 获取激活的数据源
        config = DataSourceConfig.query.filter_by(
            is_active=True,
            is_default=True
        ).first()
        
        if not config:
            return jsonify({
                'success': False,
                'message': '没有激活的数据源'
            }), 400
        
        # 根据数据源类型获取数据
        if config.source_type == 'tushare':
            token = config.config_data.get('token')
            tushare_service = TushareService(token)
            quotes = tushare_service.get_realtime_quote(ts_codes)
            
            return jsonify({
                'success': True,
                'data': quotes,
                'source': 'tushare'
            })
        
        else:
            return jsonify({
                'success': False,
                'message': f'暂不支持的数据源: {config.source_type}'
            }), 400
    
    except Exception as e:
        logger.error(f"获取实时行情失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/stocks/<string:ts_code>/daily', methods=['GET'])
def get_daily_data(ts_code):
    """获取日线数据"""
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 60, type=int)
        
        # 获取激活的数据源
        config = DataSourceConfig.query.filter_by(
            is_active=True,
            is_default=True
        ).first()
        
        if not config:
            return jsonify({
                'success': False,
                'message': '没有激活的数据源'
            }), 400
        
        # 根据数据源类型获取数据
        if config.source_type == 'tushare':
            token = config.config_data.get('token')
            tushare_service = TushareService(token)
            data = tushare_service.get_daily_data(
                ts_code,
                start_date,
                end_date,
                limit
            )
            
            return jsonify({
                'success': True,
                'data': data,
                'source': 'tushare'
            })
        
        else:
            return jsonify({
                'success': False,
                'message': f'暂不支持的数据源: {config.source_type}'
            }), 400
    
    except Exception as e:
        logger.error(f"获取日线数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
