#!/usr/bin/env python3
"""测试股票服务"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.stock_service import StockService
from loguru import logger

def test_stock_service():
    """测试股票服务"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("测试获取股票列表...")
            result = StockService.get_stock_list(page=1, page_size=10)
            logger.info(f"结果: {result}")
            
            # 直接测试从stock_minute_data表获取数据
            logger.info("\n直接测试从stock_minute_data表获取数据...")
            from app.models.stock_minute_data import StockMinuteData
            from app.extensions import db
            
            # 获取有分钟级数据的股票代码
            minute_stocks = db.session.query(StockMinuteData.ts_code).distinct().limit(10).all()
            logger.info(f"从stock_minute_data表查询到的股票代码: {minute_stocks}")
            
            total_minute_stocks = db.session.query(StockMinuteData.ts_code).distinct().count()
            logger.info(f"stock_minute_data表中不同股票总数: {total_minute_stocks}")
            
            # 获取第一只股票的最新数据
            if minute_stocks:
                ts_code = minute_stocks[0][0]
                logger.info(f"获取股票 {ts_code} 的最新数据...")
                
                latest_data = StockMinuteData.query.filter_by(ts_code=ts_code).order_by(
                    StockMinuteData.datetime.desc()
                ).first()
                
                if latest_data:
                    logger.info(f"最新数据: 时间={latest_data.datetime}, 收盘价={latest_data.close}, 涨跌幅={latest_data.pct_chg}")
                else:
                    logger.warning("没有找到最新数据")
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

if __name__ == '__main__':
    test_stock_service()