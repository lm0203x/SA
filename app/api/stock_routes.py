"""
股票数据API路由
提供股票实时数据、历史数据等接口
"""

from flask import request, jsonify
from loguru import logger
from app.api import api_bp
from app.services.stock_data_service import StockDataService


@api_bp.route('/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表（带缓存）"""
    try:
        # 获取查询参数
        industry = request.args.get('industry')
        area = request.args.get('area')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        # 从数据服务获取（会自动处理缓存）
        result = StockDataService.get_stock_list(
            industry=industry,
            area=area,
            page=page,
            page_size=page_size
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/stocks/sync', methods=['POST'])
def sync_stocks():
    """手动同步股票列表"""
    try:
        force_update = request.get_json().get('force_update', False) if request.is_json else False
        result = StockDataService.sync_stock_list(force_update=force_update)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"同步股票列表失败: {e}")
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
    """获取日线数据（带缓存）"""
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 60, type=int)
        
        # 从数据服务获取（会自动处理缓存）
        result = StockDataService.get_daily_data(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"获取日线数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/stocks/<string:ts_code>/daily/sync', methods=['POST'])
def sync_daily_data(ts_code):
    """手动同步日线数据"""
    try:
        data = request.get_json() if request.is_json else {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        result = StockDataService.sync_daily_data(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"同步日线数据失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
