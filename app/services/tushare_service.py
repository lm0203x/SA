"""
Tushare数据服务
提供Tushare Pro API的数据获取功能
"""

import tushare as ts
from datetime import datetime, timedelta
from loguru import logger
from typing import List, Dict, Optional


class TushareService:
    """Tushare数据服务类"""
    
    def __init__(self, token: str = None):
        """初始化Tushare服务"""
        self.token = token
        self.pro = None
        if token:
            try:
                ts.set_token(token)
                self.pro = ts.pro_api()
                logger.info("Tushare Pro API 初始化成功")
            except Exception as e:
                logger.error(f"Tushare Pro API 初始化失败: {e}")
    
    def test_connection(self) -> Dict:
        """测试Tushare连接"""
        try:
            if not self.pro:
                return {'success': False, 'message': 'Token未设置或无效'}
            
            # 尝试获取股票列表（只取1条）
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            
            if df is not None and not df.empty:
                return {
                    'success': True,
                    'message': '连接成功',
                    'sample_data': df.head(1).to_dict('records')[0]
                }
            else:
                return {'success': False, 'message': '无法获取数据'}
        
        except Exception as e:
            logger.error(f"Tushare连接测试失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_stock_list(self, exchange: str = '', list_status: str = 'L') -> List[Dict]:
        """
        获取股票列表
        :param exchange: 交易所代码，SSE上交所，SZSE深交所
        :param list_status: 上市状态，L上市，D退市，P暂停上市
        """
        try:
            if not self.pro:
                logger.error("Tushare Pro API未初始化")
                return []
            
            df = self.pro.stock_basic(
                exchange=exchange,
                list_status=list_status,
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            
            if df is not None and not df.empty:
                stocks = df.to_dict('records')
                logger.info(f"获取到 {len(stocks)} 只股票")
                return stocks
            else:
                logger.warning("未获取到股票数据")
                return []
        
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    def get_realtime_quote(self, ts_codes: List[str]) -> List[Dict]:
        """
        获取实时行情数据
        :param ts_codes: 股票代码列表
        """
        try:
            if not self.pro:
                logger.error("Tushare Pro API未初始化")
                return []
            
            # Tushare的实时行情需要单独获取
            quotes = []
            for ts_code in ts_codes:
                # 获取最新日线数据作为实时数据
                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=(datetime.now() - timedelta(days=7)).strftime('%Y%m%d'),
                    end_date=datetime.now().strftime('%Y%m%d')
                )
                
                if df is not None and not df.empty:
                    latest = df.iloc[0].to_dict()
                    
                    # 获取股票基本信息
                    stock_info = self.pro.stock_basic(
                        ts_code=ts_code,
                        fields='ts_code,symbol,name'
                    )
                    
                    if stock_info is not None and not stock_info.empty:
                        info = stock_info.iloc[0].to_dict()
                        latest.update(info)
                    
                    # 计算价格变化
                    if len(df) > 1:
                        prev_close = df.iloc[1]['close']
                        latest['price_change'] = round(latest['close'] - prev_close, 2)
                        latest['price_change_percent'] = round(
                            (latest['close'] - prev_close) / prev_close * 100, 2
                        )
                    else:
                        latest['price_change'] = 0
                        latest['price_change_percent'] = 0
                    
                    latest['timestamp'] = datetime.now().isoformat()
                    quotes.append(latest)
            
            return quotes
        
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return []
    
    def get_daily_data(self, ts_code: str, start_date: str = None, 
                       end_date: str = None, limit: int = 60) -> List[Dict]:
        """
        获取日线数据
        :param ts_code: 股票代码
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        :param limit: 数据条数限制
        """
        try:
            if not self.pro:
                logger.error("Tushare Pro API未初始化")
                return []
            
            # 如果没有指定日期，获取最近的数据
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=limit)).strftime('%Y%m%d')
            
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is not None and not df.empty:
                # 按日期升序排列
                df = df.sort_values('trade_date', ascending=True)
                data = df.to_dict('records')
                logger.info(f"获取到 {len(data)} 条日线数据")
                return data
            else:
                logger.warning(f"未获取到{ts_code}的日线数据")
                return []
        
        except Exception as e:
            logger.error(f"获取日线数据失败: {e}")
            return []
    
    def get_minute_data(self, ts_code: str, freq: str = '1min') -> List[Dict]:
        """
        获取分钟级数据（需要Tushare高级权限）
        :param ts_code: 股票代码
        :param freq: 频率，1min/5min/15min/30min/60min
        """
        try:
            if not self.pro:
                logger.error("Tushare Pro API未初始化")
                return []
            
            # 注意：分钟数据需要高级权限
            # 这里只是示例代码
            logger.warning("分钟级数据需要Tushare高级权限")
            return []
        
        except Exception as e:
            logger.error(f"获取分钟数据失败: {e}")
            return []
