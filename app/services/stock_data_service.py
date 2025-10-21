"""
股票数据服务
负责数据的获取、缓存和更新
"""

from datetime import datetime, timedelta
from loguru import logger
from typing import List, Dict, Optional
from sqlalchemy import and_

from app.extensions import db
from app.models.stock_basic import StockBasic
from app.models.stock_daily_history import StockDailyHistory
from app.models.stock_daily_basic import StockDailyBasic
from app.models.stock_moneyflow import StockMoneyflow
from app.models.data_source_config import DataSourceConfig
from app.services.tushare_service import TushareService


class StockDataService:
    """股票数据服务类 - 负责数据获取和缓存"""
    
    @staticmethod
    def get_active_tushare_service() -> Optional[TushareService]:
        """获取激活的Tushare服务"""
        try:
            config = DataSourceConfig.query.filter_by(
                is_active=True,
                is_default=True,
                source_type='tushare'
            ).first()
            
            if config and config.config_data and 'token' in config.config_data:
                return TushareService(config.config_data['token'])
            return None
        except Exception as e:
            logger.error(f"获取Tushare服务失败: {e}")
            return None
    
    @staticmethod
    def sync_stock_list(force_update=False) -> Dict:
        """
        同步股票列表到数据库
        :param force_update: 是否强制更新
        :return: 同步结果
        """
        try:
            # 检查是否需要更新（如果数据库有数据且不是强制更新，则跳过）
            if not force_update:
                count = StockBasic.query.count()
                if count > 0:
                    logger.info(f"数据库已有{count}只股票，跳过更新")
                    return {
                        'success': True,
                        'message': f'数据库已有{count}只股票',
                        'count': count,
                        'source': 'database'
                    }
            
            # 获取Tushare服务
            tushare_service = StockDataService.get_active_tushare_service()
            if not tushare_service:
                return {
                    'success': False,
                    'message': '未找到激活的Tushare数据源'
                }
            
            # 从Tushare获取股票列表
            logger.info("正在从Tushare获取股票列表...")
            stocks_data = tushare_service.get_stock_list()
            
            if not stocks_data:
                return {
                    'success': False,
                    'message': '未获取到股票数据'
                }
            
            # 保存到数据库
            added_count = 0
            updated_count = 0
            
            for stock_info in stocks_data:
                ts_code = stock_info.get('ts_code')
                
                # 检查是否已存在
                stock = StockBasic.query.filter_by(ts_code=ts_code).first()
                
                if stock:
                    # 更新
                    stock.symbol = stock_info.get('symbol')
                    stock.name = stock_info.get('name')
                    stock.area = stock_info.get('area')
                    stock.industry = stock_info.get('industry')
                    # list_date需要转换格式 YYYYMMDD -> Date
                    list_date_str = stock_info.get('list_date')
                    if list_date_str:
                        try:
                            stock.list_date = datetime.strptime(list_date_str, '%Y%m%d').date()
                        except:
                            stock.list_date = None
                    updated_count += 1
                else:
                    # 新增
                    list_date = None
                    list_date_str = stock_info.get('list_date')
                    if list_date_str:
                        try:
                            list_date = datetime.strptime(list_date_str, '%Y%m%d').date()
                        except:
                            pass
                    
                    stock = StockBasic(
                        ts_code=ts_code,
                        symbol=stock_info.get('symbol'),
                        name=stock_info.get('name'),
                        area=stock_info.get('area'),
                        industry=stock_info.get('industry'),
                        list_date=list_date
                    )
                    db.session.add(stock)
                    added_count += 1
            
            db.session.commit()
            logger.info(f"股票列表同步完成: 新增{added_count}只, 更新{updated_count}只")
            
            return {
                'success': True,
                'message': f'同步成功',
                'added': added_count,
                'updated': updated_count,
                'total': added_count + updated_count,
                'source': 'tushare'
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"同步股票列表失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def get_stock_list(industry=None, area=None, page=1, page_size=50) -> Dict:
        """
        获取股票列表（优先从数据库）
        :param industry: 行业筛选
        :param area: 地域筛选
        :param page: 页码
        :param page_size: 每页数量
        """
        try:
            # 构建查询
            query = StockBasic.query
            
            if industry:
                query = query.filter(StockBasic.industry == industry)
            if area:
                query = query.filter(StockBasic.area == area)
            
            # 总数
            total = query.count()
            
            # 如果数据库没有数据，尝试同步
            if total == 0:
                logger.info("数据库无股票数据，尝试同步...")
                sync_result = StockDataService.sync_stock_list()
                if sync_result['success']:
                    # 重新查询
                    query = StockBasic.query
                    if industry:
                        query = query.filter(StockBasic.industry == industry)
                    if area:
                        query = query.filter(StockBasic.area == area)
                    total = query.count()
            
            # 分页
            stocks = query.offset((page - 1) * page_size).limit(page_size).all()
            
            return {
                'success': True,
                'data': [stock.to_dict() for stock in stocks],
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'source': 'database'
            }
        
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return {
                'success': False,
                'message': str(e),
                'data': [],
                'total': 0
            }
    
    @staticmethod
    def sync_daily_data(ts_code: str, start_date: str = None, end_date: str = None) -> Dict:
        """
        同步日线数据到数据库
        :param ts_code: 股票代码
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        """
        try:
            # 获取Tushare服务
            tushare_service = StockDataService.get_active_tushare_service()
            if not tushare_service:
                return {
                    'success': False,
                    'message': '未找到激活的Tushare数据源'
                }
            
            # 从Tushare获取数据
            daily_data = tushare_service.get_daily_data(ts_code, start_date, end_date)
            
            if not daily_data:
                return {
                    'success': False,
                    'message': '未获取到日线数据'
                }
            
            # 保存到数据库
            added_count = 0
            
            # 数据清洗函数：将NaN值转换为None
            def clean_value(value):
                import math
                if value is None:
                    return None
                if isinstance(value, (int, float)) and math.isnan(value):
                    return None
                return value
            
            for data in daily_data:
                trade_date = data.get('trade_date')
                
                # 检查是否已存在
                existing = StockDailyHistory.query.filter_by(
                    ts_code=ts_code,
                    trade_date=trade_date
                ).first()
                
                if not existing:
                    daily = StockDailyHistory(
                        ts_code=ts_code,
                        trade_date=trade_date,
                        open=clean_value(data.get('open')),
                        high=clean_value(data.get('high')),
                        low=clean_value(data.get('low')),
                        close=clean_value(data.get('close')),
                        pre_close=clean_value(data.get('pre_close')),
                        change_c=clean_value(data.get('change')),
                        pct_chg=clean_value(data.get('pct_chg')),
                        vol=clean_value(data.get('vol')),
                        amount=clean_value(data.get('amount'))
                    )
                    db.session.add(daily)
                    added_count += 1
            
            db.session.commit()
            logger.info(f"同步{ts_code}日线数据完成: 新增{added_count}条")
            
            return {
                'success': True,
                'message': '同步成功',
                'added': added_count,
                'source': 'tushare'
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"同步日线数据失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def get_daily_data(ts_code: str, start_date: str = None, end_date: str = None, limit: int = 60) -> Dict:
        """
        获取日线数据（优先从数据库）
        :param ts_code: 股票代码
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        :param limit: 数据条数
        """
        try:
            # 构建查询
            query = StockDailyHistory.query.filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(StockDailyHistory.trade_date >= start_date)
            if end_date:
                query = query.filter(StockDailyHistory.trade_date <= end_date)
            
            # 查询数据库
            daily_data = query.order_by(StockDailyHistory.trade_date.desc()).limit(limit).all()
            
            # 如果数据库没有数据，从Tushare获取并保存
            if not daily_data:
                logger.info(f"数据库无{ts_code}的日线数据，从Tushare获取...")
                sync_result = StockDataService.sync_daily_data(ts_code, start_date, end_date)
                
                if sync_result['success']:
                    # 重新查询
                    query = StockDailyHistory.query.filter_by(ts_code=ts_code)
                    if start_date:
                        query = query.filter(StockDailyHistory.trade_date >= start_date)
                    if end_date:
                        query = query.filter(StockDailyHistory.trade_date <= end_date)
                    daily_data = query.order_by(StockDailyHistory.trade_date.desc()).limit(limit).all()
            
            return {
                'success': True,
                'data': [d.to_dict() for d in daily_data],
                'source': 'database'
            }
        
        except Exception as e:
            logger.error(f"获取日线数据失败: {e}")
            return {
                'success': False,
                'message': str(e),
                'data': []
            }
    
    @staticmethod
    def sync_daily_basic(ts_code: str, start_date: str = None, end_date: str = None) -> Dict:
        """
        同步每日指标数据到数据库
        :param ts_code: 股票代码
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        """
        try:
            # 获取Tushare服务
            tushare_service = StockDataService.get_active_tushare_service()
            if not tushare_service:
                return {
                    'success': False,
                    'message': '未找到激活的Tushare数据源'
                }
            
            # 从Tushare获取数据
            basic_data = tushare_service.get_daily_basic(ts_code, start_date, end_date)
            
            if not basic_data:
                return {
                    'success': False,
                    'message': '未获取到每日指标数据'
                }
            
            # 保存到数据库
            added_count = 0
            
            for data in basic_data:
                trade_date_str = data.get('trade_date')
                if not trade_date_str:
                    continue
                
                # 转换日期格式 YYYYMMDD -> Date
                try:
                    trade_date = datetime.strptime(trade_date_str, '%Y%m%d').date()
                except:
                    continue
                
                # 检查是否已存在
                existing = StockDailyBasic.query.filter_by(
                    ts_code=ts_code,
                    trade_date=trade_date
                ).first()
                
                if not existing:
                    # 数据清洗：将NaN值转换为None
                    def clean_value(value):
                        import math
                        if value is None:
                            return None
                        if isinstance(value, (int, float)) and math.isnan(value):
                            return None
                        return value
                    
                    basic = StockDailyBasic(
                        ts_code=ts_code,
                        trade_date=trade_date,
                        close=clean_value(data.get('close')),
                        turnover_rate=clean_value(data.get('turnover_rate')),
                        turnover_rate_f=clean_value(data.get('turnover_rate_f')),
                        volume_ratio=clean_value(data.get('volume_ratio')),
                        pe=clean_value(data.get('pe')),
                        pe_ttm=clean_value(data.get('pe_ttm')),
                        pb=clean_value(data.get('pb')),
                        ps=clean_value(data.get('ps')),
                        ps_ttm=clean_value(data.get('ps_ttm')),
                        dv_ratio=clean_value(data.get('dv_ratio')),
                        dv_ttm=clean_value(data.get('dv_ttm')),
                        total_share=clean_value(data.get('total_share')),
                        float_share=clean_value(data.get('float_share')),
                        free_share=clean_value(data.get('free_share')),
                        total_mv=clean_value(data.get('total_mv')),
                        circ_mv=clean_value(data.get('circ_mv'))
                    )
                    db.session.add(basic)
                    added_count += 1
            
            db.session.commit()
            logger.info(f"同步{ts_code}每日指标完成: 新增{added_count}条")
            
            return {
                'success': True,
                'message': '同步成功',
                'added': added_count,
                'source': 'tushare'
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"同步每日指标失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def get_daily_basic(ts_code: str, start_date: str = None, end_date: str = None, limit: int = 60) -> Dict:
        """
        获取每日指标数据（优先从数据库）
        :param ts_code: 股票代码
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        :param limit: 数据条数
        """
        try:
            # 构建查询
            query = StockDailyBasic.query.filter_by(ts_code=ts_code)
            
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y%m%d').date()
                query = query.filter(StockDailyBasic.trade_date >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y%m%d').date()
                query = query.filter(StockDailyBasic.trade_date <= end_date_obj)
            
            # 查询数据库
            basic_data = query.order_by(StockDailyBasic.trade_date.desc()).limit(limit).all()
            
            # 如果数据库没有数据，从Tushare获取并保存
            if not basic_data:
                logger.info(f"数据库无{ts_code}的每日指标数据，从Tushare获取...")
                sync_result = StockDataService.sync_daily_basic(ts_code, start_date, end_date)
                
                if sync_result['success']:
                    # 重新查询
                    query = StockDailyBasic.query.filter_by(ts_code=ts_code)
                    if start_date:
                        start_date_obj = datetime.strptime(start_date, '%Y%m%d').date()
                        query = query.filter(StockDailyBasic.trade_date >= start_date_obj)
                    if end_date:
                        end_date_obj = datetime.strptime(end_date, '%Y%m%d').date()
                        query = query.filter(StockDailyBasic.trade_date <= end_date_obj)
                    basic_data = query.order_by(StockDailyBasic.trade_date.desc()).limit(limit).all()
            
            return {
                'success': True,
                'data': [d.to_dict() for d in basic_data],
                'source': 'database'
            }
        
        except Exception as e:
            logger.error(f"获取每日指标失败: {e}")
            return {
                'success': False,
                'message': str(e),
                'data': []
            }
    
    @staticmethod
    def sync_moneyflow(ts_code: str, start_date: str = None, end_date: str = None) -> Dict:
        """
        同步资金流向数据到数据库
        :param ts_code: 股票代码
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        """
        try:
            # 获取Tushare服务
            tushare_service = StockDataService.get_active_tushare_service()
            if not tushare_service:
                return {
                    'success': False,
                    'message': '未找到激活的Tushare数据源'
                }
            
            # 从Tushare获取数据
            moneyflow_data = tushare_service.get_moneyflow(ts_code, start_date, end_date)
            
            if not moneyflow_data:
                return {
                    'success': False,
                    'message': '未获取到资金流向数据'
                }
            
            # 保存到数据库
            added_count = 0
            
            # 数据清洗函数：将NaN值转换为None
            def clean_value(value):
                import math
                if value is None:
                    return None
                if isinstance(value, (int, float)) and math.isnan(value):
                    return None
                return value
            
            for data in moneyflow_data:
                trade_date_str = data.get('trade_date')
                if not trade_date_str:
                    continue
                
                # 转换日期格式 YYYYMMDD -> Date
                try:
                    trade_date = datetime.strptime(trade_date_str, '%Y%m%d').date()
                except:
                    continue
                
                # 检查是否已存在
                existing = StockMoneyflow.query.filter_by(
                    ts_code=ts_code,
                    trade_date=trade_date
                ).first()
                
                if not existing:
                    moneyflow = StockMoneyflow(
                        ts_code=ts_code,
                        trade_date=trade_date,
                        buy_sm_vol=clean_value(data.get('buy_sm_vol')),
                        buy_sm_amount=clean_value(data.get('buy_sm_amount')),
                        sell_sm_vol=clean_value(data.get('sell_sm_vol')),
                        sell_sm_amount=clean_value(data.get('sell_sm_amount')),
                        buy_md_vol=clean_value(data.get('buy_md_vol')),
                        buy_md_amount=clean_value(data.get('buy_md_amount')),
                        sell_md_vol=clean_value(data.get('sell_md_vol')),
                        sell_md_amount=clean_value(data.get('sell_md_amount')),
                        buy_lg_vol=clean_value(data.get('buy_lg_vol')),
                        buy_lg_amount=clean_value(data.get('buy_lg_amount')),
                        sell_lg_vol=clean_value(data.get('sell_lg_vol')),
                        sell_lg_amount=clean_value(data.get('sell_lg_amount')),
                        buy_elg_vol=clean_value(data.get('buy_elg_vol')),
                        buy_elg_amount=clean_value(data.get('buy_elg_amount')),
                        sell_elg_vol=clean_value(data.get('sell_elg_vol')),
                        sell_elg_amount=clean_value(data.get('sell_elg_amount')),
                        net_mf_vol=clean_value(data.get('net_mf_vol')),
                        net_mf_amount=clean_value(data.get('net_mf_amount'))
                    )
                    db.session.add(moneyflow)
                    added_count += 1
            
            db.session.commit()
            logger.info(f"同步{ts_code}资金流向完成: 新增{added_count}条")
            
            return {
                'success': True,
                'message': '同步成功',
                'added': added_count,
                'source': 'tushare'
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"同步资金流向失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def get_moneyflow(ts_code: str, start_date: str = None, end_date: str = None, limit: int = 30) -> Dict:
        """
        获取资金流向数据（优先从数据库）
        :param ts_code: 股票代码
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        :param limit: 数据条数
        """
        try:
            # 构建查询
            query = StockMoneyflow.query.filter_by(ts_code=ts_code)
            
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y%m%d').date()
                query = query.filter(StockMoneyflow.trade_date >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y%m%d').date()
                query = query.filter(StockMoneyflow.trade_date <= end_date_obj)
            
            # 查询数据库
            moneyflow_data = query.order_by(StockMoneyflow.trade_date.desc()).limit(limit).all()
            
            # 如果数据库没有数据，从Tushare获取并保存
            if not moneyflow_data:
                logger.info(f"数据库无{ts_code}的资金流向数据，从Tushare获取...")
                sync_result = StockDataService.sync_moneyflow(ts_code, start_date, end_date)
                
                if sync_result['success']:
                    # 重新查询
                    query = StockMoneyflow.query.filter_by(ts_code=ts_code)
                    if start_date:
                        start_date_obj = datetime.strptime(start_date, '%Y%m%d').date()
                        query = query.filter(StockMoneyflow.trade_date >= start_date_obj)
                    if end_date:
                        end_date_obj = datetime.strptime(end_date, '%Y%m%d').date()
                        query = query.filter(StockMoneyflow.trade_date <= end_date_obj)
                    moneyflow_data = query.order_by(StockMoneyflow.trade_date.desc()).limit(limit).all()
            
            return {
                'success': True,
                'data': [d.to_dict() for d in moneyflow_data],
                'source': 'database'
            }
        
        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return {
                'success': False,
                'message': str(e),
                'data': []
            }
